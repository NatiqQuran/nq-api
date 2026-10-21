from rest_framework import permissions, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)
from django_filters.rest_framework import DjangoFilterBackend
from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Takhtit, AyahBreaker, Ayah, Surah
from quran.serializers import (
    TakhtitSerializer,
    AyahBreakerSerializer,
    AyahBreakersResponseSerializer,
    WordBreakersResponseSerializer,
    WordBreakerDetailResponseSerializer,
)


class DictCompare:
    def __init__(self, first_dict, second_dict):
        self.first = first_dict
        self.second = second_dict

    def update_second_dict(self, new_second):
        self.second = new_second

    def compare_two_dicts_with_condition(self, condition):
        """
        condition: function
        """
        for k, v in self.second.items():
            same_key = self.first.get(k)
            if same_key and v and condition(same_key, v):
                return False
        return True


@extend_schema_view(
    list=extend_schema(
        summary="List all Takhtits (text annotations/notes)",
        parameters=[
            OpenApiParameter(
                name="mushaf",
                type={"type": "string", "enum": ["hafs"]},
                location=OpenApiParameter.QUERY,
                required=False,
                description="Short name of the Mushaf to filter Takhtits by. Common value: 'hafs'. Any string is accepted. (e.g. 'hafs', 'warsh', etc.)",
            )
        ],
        tags=["general", "takhtits"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific Takhtit by id", tags=["general", "takhtits"]
    ),
    create=extend_schema(
        summary="Create a new Takhtit record",
        description="Create a new Takhtit. Requires mushaf_id and account_id in the request body.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "mushaf_id": {
                        "type": "string",
                        "format": "id",
                        "description": "id of the mushaf to link.",
                    },
                    "account_id": {
                        "type": "string",
                        "format": "id",
                        "description": "id of the account to link.",
                    },
                },
                "required": ["mushaf_id", "account_id"],
            }
        },
    ),
    update=extend_schema(summary="Update an existing Takhtit record"),
    partial_update=extend_schema(summary="Partially update a Takhtit record"),
    destroy=extend_schema(summary="Delete a Takhtit record"),
)
class TakhtitViewSet(viewsets.ModelViewSet):
    queryset = Takhtit.objects.all()
    serializer_class = TakhtitSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions,
    ]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    pagination_class = CustomLimitOffsetPagination
    filterset_fields = ["rasm_ol_mushaf", "account", "creator"]
    search_fields = []
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    lookup_field = "id"

    def perform_create(self, serializer):
        rasm_ol_mushaf = self.request.data.get("rasm_ol_mushaf")
        account_id = self.request.data.get("account")
        from quran.models import RasmOlMushaf
        from account.models import CustomUser

        mushaf = None
        account = None
        errors = {}
        if not rasm_ol_mushaf:
            errors["rasm_ol_mushaf"] = "This field is required."
        else:
            try:
                mushaf = RasmOlMushaf.objects.get(id=rasm_ol_mushaf)
            except RasmOlMushaf.DoesNotExist:
                errors["rasm_ol_mushaf"] = "Mushaf not found."
        if not account_id:
            errors["account"] = "This field is required."
        else:
            try:
                account = CustomUser.objects.get(id=account_id)
            except CustomUser.DoesNotExist:
                errors["account_id"] = "Account not found."
        if errors:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(errors)
        serializer.save(
            creator=self.request.user, rasm_ol_mushaf=mushaf, account=account
        )

    @extend_schema(
        summary="List all ayahs_breakers for this takhtit (ayahs map style)",
        description="Returns a flat list containing an entry for every ayah in this takhtit, with breaker info similar to the mushaf ayah_map action.",
        responses={200: AyahBreakersResponseSerializer(many=True)},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="ayahs_breakers",
    )
    def ayahs_breakers(self, request, id=None):
        breaker_keys = ["page", "juz", "hizb", "rub", "manzil"]

        into_int_or_none = lambda x: int(x) if (x is not None) else x

        # Dict of filters
        filters = {
            key: into_int_or_none(self.request.query_params.get(key))
            for key in breaker_keys
        }

        takhtit = self.get_object()
        ayah_ids = AyahBreaker.objects.filter(takhtit=takhtit).values_list(
            "ayah_id", flat=True
        )

        ayah_qs = (
            Ayah.objects.select_related("surah")
            .prefetch_related("words")
            .order_by("surah__number", "number", "id")
        )

        breakers_qs = (
            AyahBreaker.objects.filter(takhtit=takhtit, ayah__in=ayah_qs)
            .select_related("ayah", "ayah__surah")
            .order_by("ayah__surah__number", "ayah__number")
        )

        from collections import defaultdict

        # If the breaker value is 0 then return None
        # Else return the breaker
        breaker_or_none = lambda x: (x != 0 and x) or None

        breakers_by_ayah = defaultdict(list)
        for br in breakers_qs:
            breakers_by_ayah[br.ayah_id].append(br.type.lower())
        counters = {k: 0 for k in breaker_keys}
        data = []
        dc = DictCompare(filters, counters)

        for ayah in ayah_qs:
            for br_type in breakers_by_ayah.get(ayah.id, []):
                key = br_type.split()[0]
                if key in counters:
                    counters[key] += 1
            dc.update_second_dict(counters)
            last_compare = dc.compare_two_dicts_with_condition(lambda x, y: x < y)
            if not last_compare:
                break

            if dc.compare_two_dicts_with_condition(lambda x, y: x != y):
                data.append(
                    {
                        "id": str(ayah.id),
                        "surah_id": ayah.surah.id,
                        "surah_number": ayah.surah.number,
                        "ayah_number": ayah.number,
                        "length": ayah.length,
                        "juz": breaker_or_none(counters["juz"]),
                        "hizb": breaker_or_none(counters["hizb"]),
                        "page": breaker_or_none(counters["page"]),
                        "rub": breaker_or_none(counters["rub"]),
                        "manzil": breaker_or_none(counters["manzil"]),
                    }
                )
        paginator = CustomLimitOffsetPagination()
        page = paginator.paginate_queryset(data, request)
        return Response(page)

    @extend_schema(
        summary="Add an ayahs_breaker to this takhtit",
        description="Add a new ayahs_breaker to this takhtit. Requires ayah_id in the request body.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "ayah_id": {
                        "type": "string",
                        "format": "id",
                        "description": "id of the ayah to link.",
                    },
                    "type": {
                        "type": "string",
                        "description": "Breaker type (see AyahBreakerType).",
                    },
                },
                "required": ["ayah_id", "type"],
            }
        },
        responses={201: AyahBreakerSerializer},
    )
    @ayahs_breakers.mapping.post
    def add_ayahs_breaker(self, request, id=None):
        takhtit = self.get_object()
        data = request.data.copy()
        ayah_id = data.pop("ayah_id", None)
        breaker_type = data.get("type")
        if not ayah_id:
            return Response(
                {"detail": "ayah_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not breaker_type:
            return Response(
                {"detail": "type is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        from quran.models import Ayah, AyahBreakerType

        valid_types = [choice[0] for choice in AyahBreakerType.choices]
        if breaker_type not in valid_types:
            return Response(
                {"detail": f"Invalid type. Must be one of: {', '.join(valid_types)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            ayah = Ayah.objects.get(id=ayah_id)
        except Ayah.DoesNotExist:
            return Response(
                {"detail": "Ayah not found."}, status=status.HTTP_404_NOT_FOUND
            )
        data["takhtit"] = takhtit.pk
        data["ayah"] = ayah.pk
        serializer = AyahBreakerSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Retrieve a specific ayahs_breaker for this takhtit",
        parameters=[
            OpenApiParameter(
                name="breaker_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description="id of the ayahs_breaker.",
            )
        ],
        responses={200: AyahBreakerSerializer, 404: OpenApiTypes.OBJECT},
    )
    @action(
        detail=True, methods=["get"], url_path="ayahs_breakers/(?P<breaker_id>[^/.]+)"
    )
    def retrieve_ayahs_breaker(self, request, id=None, breaker_id=None):
        takhtit = self.get_object()
        breaker = AyahBreaker.objects.filter(takhtit=takhtit, id=breaker_id).first()
        if not breaker:
            return Response({"detail": "AyahBreaker not found."}, status=404)
        serializer = AyahBreakerSerializer(breaker)
        return Response(serializer.data)

    @extend_schema(
        summary="List all words_breakers for this takhtit (with line counters)",
        description="Returns a flat list containing an entry for every word with a breaker for this takhtit, with a line counter (incremented for each breaker).",
        responses={200: WordBreakersResponseSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="words_breakers")
    def words_breakers(self, request, id=None):
        takhtit = self.get_object()
        from quran.models import WordBreaker, Word

        word_breakers = (
            WordBreaker.objects.filter(takhtit=takhtit)
            .select_related("word", "word__ayah")
            .order_by("word__ayah__surah__number", "word__ayah__number", "word__id")
        )
        line_counter = 0
        data = []
        for wb in word_breakers:
            line_counter += 1
            data.append({"word_id": str(wb.word.id), "line": line_counter})
        return Response(data)

    @extend_schema(
        summary="Add a words_breaker to this takhtit",
        description="Add a new words_breaker to this takhtit. Requires word_id in the request body. Only type 'line' is allowed.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "word_id": {
                        "type": "string",
                        "format": "id",
                        "description": "id of the word to link.",
                    },
                    "type": {
                        "type": "string",
                        "description": "Breaker type (must be 'line').",
                    },
                },
                "required": ["word_id", "type"],
            }
        },
        responses={201: WordBreakerDetailResponseSerializer},
    )
    @words_breakers.mapping.post
    def add_words_breaker(self, request, id=None):
        takhtit = self.get_object()
        data = request.data.copy()
        word_id = data.pop("word_id", None)
        breaker_type = data.get("type")
        if not word_id:
            return Response(
                {"detail": "word_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not breaker_type:
            return Response(
                {"detail": "type is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if breaker_type != "line":
            return Response(
                {"detail": "Invalid type. Only 'line' is allowed for WordBreaker."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from quran.models import Word, WordBreaker

        try:
            word = Word.objects.get(id=word_id)
        except Word.DoesNotExist:
            return Response(
                {"detail": "Word not found."}, status=status.HTTP_404_NOT_FOUND
            )
        WordBreaker.objects.create(
            creator=request.user, word=word, takhtit=takhtit, type="line"
        )
        return Response(
            {"word_id": str(word.id), "type": "line"}, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Retrieve a specific words_breaker for this takhtit",
        parameters=[
            OpenApiParameter(
                name="breaker_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description="id of the words_breaker.",
            )
        ],
        responses={200: WordBreakerDetailResponseSerializer, 404: OpenApiTypes.OBJECT},
    )
    @action(
        detail=True, methods=["get"], url_path="words_breakers/(?P<breaker_id>[^/.]+)"
    )
    def retrieve_words_breaker(self, request, id=None, breaker_id=None):
        from quran.models import WordBreaker

        takhtit = self.get_object()
        breaker = WordBreaker.objects.filter(takhtit=takhtit, id=breaker_id).first()
        if not breaker:
            return Response({"detail": "WordBreaker not found."}, status=404)
        return Response({"word_id": str(breaker.word.id), "type": breaker.type})

    @extend_schema(
        summary="Import Ayah Breakers for the specified Takhtit",
        description=(
            "Accepts a JSON array of strings with the format '{surah}:{ayah}' that denote the ayah at which a new breaker (page by default) begins. Existing breakers whose names start with the provided breaker type (default: 'page') will be removed before importing the new ones."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Text/JSON file containing a list of breakers (e.g. ['2:1', '2:6']).",
                    }
                },
                "required": ["file"],
            }
        },
        methods=["POST"],
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Breaker type (e.g., page, juz, hizb). Defaults to 'page'.",
            )
        ],
        responses={201: OpenApiTypes.OBJECT},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_breakers(self, request, id=None):
        import json
        from quran.models import Ayah, AyahBreaker, Surah

        takhtit = self.get_object()
        breaker_type = request.query_params.get("type", "page")
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            data = json.load(file)
        except Exception as e:
            return Response(
                {"detail": f"Invalid file: {e}"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(data, list):
            return Response(
                {"detail": "File must contain a list of breakers."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        AyahBreaker.objects.filter(takhtit=takhtit, type=breaker_type).delete()
        created = 0
        for item in data:
            try:
                surah_num, ayah_num = map(int, item.split(":"))
                surah = (
                    Surah.objects.filter(
                        number=surah_num,
                        rom_surah_ayahs_surah__rasm_ol_mushaf=takhtit.rasm_ol_mushaf,
                    )
                    .distinct()
                    .get()
                )
                ayah = Ayah.objects.get(surah=surah, number=ayah_num)
                AyahBreaker.objects.create(
                    ayah=ayah, takhtit=takhtit, type=breaker_type, creator=request.user
                )
                created += 1
            except Exception as e:
                print("ERR:", e)
                return Response({"error": "internal"}, status=500)
        return Response({"created": created}, status=status.HTTP_201_CREATED)
