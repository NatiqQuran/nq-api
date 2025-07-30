from rest_framework import permissions, viewsets, status, filters
from rest_framework.response import Response
from quran.models import (
    Mushaf,
    Surah,
    Ayah,
    Word,
    Translation,
    AyahTranslation,
    Recitation,
    AyahBreaker,
    RecitationSurah,
    RecitationSurahTimestamp,
)
from quran.serializers import (
    AyahSerializerView,
    MushafSerializer,
    SurahSerializer,
    SurahDetailSerializer,
    AyahSerializer,
    WordSerializer,
    TranslationSerializer,
    AyahTranslationSerializer,
    AyahAddSerializer,
    RecitationSerializer,
    TranslationListSerializer,
)

from core import permissions as core_permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from core.pagination import CustomPageNumberPagination
from rest_framework.decorators import action
import json
from rest_framework.parsers import MultiPartParser, FormParser
from quran.models import RecitationSurahTimestamp
from rest_framework import serializers

@extend_schema_view(
    list=extend_schema(summary="List all Mushafs (Quranic manuscripts/editions)", tags=["general", "mushafs"]),
    retrieve=extend_schema(summary="Retrieve a specific Mushaf by UUID", tags=["general", "mushafs"]),
    create=extend_schema(summary="Create a new Mushaf record"),
    update=extend_schema(summary="Update an existing Mushaf record"),
    partial_update=extend_schema(summary="Partially update a Mushaf record"),
    destroy=extend_schema(summary="Delete a Mushaf record")
)
class MushafViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Mushaf objects (Quranic manuscripts/editions).
    Supports listing, creating, updating, and retrieving Mushaf records.
    Enforces permissions and restricts editing of published Mushafs.
    """
    queryset = Mushaf.objects.all().order_by('short_name')
    serializer_class = MushafSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions,
        core_permissions.LimitedFieldEditPermission
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["short_name", "name", "source"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination  # Fixed typo
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"

    # --- NEW ACTION: Ayah map for a Mushaf ---
    @extend_schema(
        summary="Map of all ayahs for the specified Mushaf",
        description=(
            "Returns a flat list containing an entry for **every** ayah that belongs to the selected "
            "mushaf. The response schema is:\n"
            "```json\n[\n  {\n    \"uuid\": \"str\",            // Ayah UUID\n    \"surah\": \"int\",           // Surah number\n    \"ayah\": \"int\",            // Ayah number within the surah\n    \"juz\": \"int|null\",        // Juz number (null if unknown)\n    \"hizb\": \"int|null\",       // Hizb quarter number (null if unknown)\n    \"ruku\": \"int|null\",       // Ruku number (null if unknown)\n    \"page\": \"int|null\"        // Page number in the standard Madinah mushaf (null if unknown)\n  },\n  ...\n]\n```"
        ),
        methods=["GET"],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["get"], url_path="map")
    def ayah_map(self, request, *args, **kwargs):
        """Return a simplified mapping of every ayah for the specified Mushaf UUID (path param)."""
        mushaf = self.get_object()

        # Gather all ayahs (ordered) once
        ayah_qs = (
            Ayah.objects.filter(surah__mushaf=mushaf)
            .select_related("surah")
            .order_by("surah__number", "number", "id")
        )

        # Fetch Ayah-level breakers only for these ayahs
        breakers_qs = (
            AyahBreaker.objects
            .filter(ayah__in=ayah_qs)
            .select_related("ayah", "ayah__surah")
            .order_by("ayah__surah__number", "ayah__number")
        )

        # Group breakers by ayah_id for O(1) lookup per iteration
        from collections import defaultdict
        breakers_by_ayah = defaultdict(list)
        for br in breakers_qs:
            breakers_by_ayah[br.ayah_id].append(br.name.lower())

        # Running counters for each breaker type
        counters = {"juz": 0, "hizb": 0, "ruku": 0, "page": 0}

        data = []
        for ayah in ayah_qs:
            # Increment counters for breakers that BEGIN at this ayah
            for br_name in breakers_by_ayah.get(ayah.id, []):
                key = br_name.split()[0]  # take first token (e.g. "juz", "hizb")
                if key in counters:
                    counters[key] += 1

            data.append({
                "uuid": str(ayah.uuid),
                "surah": ayah.surah.number,
                "ayah": ayah.number,
                "juz": counters["juz"] or None,
                "hizb": counters["hizb"] or None,
                "ruku": counters["ruku"] or None,
                "page": counters["page"] or None,
            })

        return Response(data)

    # --- END NEW ACTION ---

    # --- NEW ACTION: Import ayah breakers (e.g., pages) for a Mushaf ---
    @extend_schema(
        summary="Import Ayah Breakers for the specified Mushaf",
        description=(
            "Accepts a JSON array of strings with the format \"{surah}:{ayah}\" that denote the ayah "
            "at which a new breaker (page by default) begins. Existing breakers whose names start with the "
            "provided breaker type (default: 'page') will be removed before importing the new ones.\n\n"
            "Example request body (application/json):\n\n"
            "[\n  \"2:1\",\n  \"2:6\",\n  \"2:17\"\n]"
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Text/JSON file containing a list of breakers (e.g. ['2:1', '2:6'])."
                    }
                },
                "required": ["file"]
            }
        },
        methods=["POST"],
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Breaker type (e.g., page, juz, hizb, ruku). Defaults to 'page'.",
            ),
        ],
        responses={201: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["post"], url_path="import_breakers", parser_classes=[MultiPartParser, FormParser])
    def import_breakers(self, request, *args, **kwargs):
        """Import (upsert) ayah breakers for this Mushaf.

        The endpoint expects the request body to be a JSON list of strings, each representing the
        starting ayah of a breaker in the form "{surah}:{ayah}". Only the first token in the breaker
        name is significant for the existing `ayah_map` logic, so breakers will be named using the
        pattern "{breaker_type} {index}", where `breaker_type` defaults to "page".
        """
        from django.db import transaction
        mushaf = self.get_object()

        breaker_type = request.query_params.get("type", "page").lower()

        # Expect a file upload similar to other import endpoints
        BREAKERS_UPLOAD_MAX_SIZE = 5 * 1024 * 1024  # 5 MB should be plenty
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > BREAKERS_UPLOAD_MAX_SIZE:
            return Response({"detail": f"File size exceeds the {BREAKERS_UPLOAD_MAX_SIZE} bytes limit."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = file.read().decode("utf-8").strip()
            # Try JSON first
            import json as _json
            breakers_input = _json.loads(content)
            if not isinstance(breakers_input, list):
                raise ValueError
        except Exception:
            # Fallback: treat as newline-separated list
            breakers_input = [line.strip() for line in content.splitlines() if line.strip()]

        if not breakers_input:
            return Response({"detail": "No breaker entries found in file."}, status=status.HTTP_400_BAD_REQUEST)

        # Build lookup for surahs within this mushaf to avoid repeated DB hits
        surahs_by_number = {
            s.number: s for s in Surah.objects.filter(mushaf=mushaf).only("id", "number")
        }

        created, errors = 0, []

        with transaction.atomic():
            # Remove existing breakers for this mushaf of the same type to avoid duplicates
            AyahBreaker.objects.filter(
                ayah__surah__mushaf=mushaf, name__istartswith=breaker_type
            ).delete()

            for idx, ref in enumerate(breakers_input, start=1):
                try:
                    surah_num_str, ayah_num_str = ref.split(":", 1)
                    surah_num = int(surah_num_str)
                    ayah_num = int(ayah_num_str)
                except (ValueError, AttributeError):
                    errors.append({"entry": ref, "error": "Invalid format, expected 'surah:ayah'."})
                    continue

                surah = surahs_by_number.get(surah_num)
                if not surah:
                    errors.append({"entry": ref, "error": f"Surah {surah_num} not found in mushaf."})
                    continue

                try:
                    ayah = Ayah.objects.only("id").get(surah=surah, number=ayah_num)
                except Ayah.DoesNotExist:
                    errors.append({"entry": ref, "error": f"Ayah {ayah_num} not found in surah {surah_num}."})
                    continue

                AyahBreaker.objects.create(
                    creator=request.user,
                    ayah=ayah,
                    name=f"{breaker_type}"
                )
                created += 1

        return Response(
            {
                "detail": f"Imported {created} {breaker_type} breakers.",
                "created": created,
                "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )

    # --- END NEW ACTION ---

    def get_queryset(self):
        # Optimize: Only fetch fields needed for the list action
        if getattr(self, 'action', None) == 'list':
            return Mushaf.objects.only('uuid', 'short_name', 'name', 'source', 'status').order_by('short_name')
        # For retrieve and others, fetch all fields
        return Mushaf.objects.all().order_by('short_name')
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Allow admin users to edit even if published
        if instance.status == 'published' and not request.user.is_staff:
            return Response({'detail': 'Published Mushaf cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)
        status_value = request.data.get('status')
        if status_value == 'pending_review':
            # Count ayahs for this mushaf
            ayah_count = Ayah.objects.filter(surah__mushaf=instance).count()
            ayah_translation_count = AyahTranslation.objects.filter(translation__mushaf=instance).count()
            if ayah_translation_count != ayah_count:
                return Response({
                    'detail': f'Mushaf is incomplete: {ayah_translation_count} of {ayah_count} ayahs translated.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, partial=partial, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary", "description": "JSON file containing the Mushaf data"}
                },
                "required": ["file"]
            }
        },
        summary="Import a Mushaf from a JSON file upload"
    )
    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser, FormParser])
    def import_mushaf(self, request):
        from django.db import transaction
        MUSHAF_UPLOAD_MAX_SIZE = 30 * 1024 * 1024
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > MUSHAF_UPLOAD_MAX_SIZE:
            return Response(
                {'error': f'File size exceeds the maximum allowed for mushaf import ({MUSHAF_UPLOAD_MAX_SIZE} bytes, got {file.size} bytes).'},
                status=400
            )
        if not file.name.lower().endswith('.json'):
            return Response({'detail': 'Only JSON files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quran_data = json.load(file)
            user = request.user
            from quran.tasks import import_mushaf_task
            import_mushaf_task.delay(quran_data, user.id)
            return Response({'detail': 'Mushaf import started. You will be notified when it is complete.'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        summary="List all Surahs (Quran chapters)",
        parameters=[
            OpenApiParameter(
                name="mushaf",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Short name of the Mushaf to filter Surahs by."
            )
        ],
        tags=["general", "surahs"],
    ),
    retrieve=extend_schema(summary="Retrieve a specific Surah by UUID", tags=["general", "surahs"]),
    create=extend_schema(summary="Create a new Surah record"),
    update=extend_schema(summary="Update an existing Surah record"),
    partial_update=extend_schema(summary="Partially update a Surah record"),
    destroy=extend_schema(summary="Delete a Surah record")
)
class SurahViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Surah (chapter) objects of the Quran.
    Allows filtering by Mushaf, searching by name, and auto-increments Surah number on creation.
    """
    queryset = Surah.objects.all().order_by('number')
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        core_permissions.IsCreatorOfParentOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    lookup_field = "uuid"

    def get_parent_for_permission(self, request):
        """
        For create requests, return the Mushaf object to check ownership.
        This is used by IsCreatorOrReadOnly permission.
        """
        mushaf_uuid = request.data.get('mushaf_uuid', None)
        if mushaf_uuid:
            return Mushaf.objects.filter(uuid=mushaf_uuid).first()
        return None

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurahDetailSerializer
        return SurahSerializer
    
    def get_queryset(self):
        surah_fields = [
            'uuid', 'mushaf', 'name', 'number', 'period', 'name_pronunciation', 'name_translation', 'name_transliteration', 'search_terms', 'creator'
        ]
        queryset = Surah.objects.all()
        if self.action == 'retrieve':
            queryset = queryset.select_related('mushaf').prefetch_related('ayahs__words').only(*surah_fields)
        else:
            queryset = queryset.select_related('mushaf').only(*surah_fields)
        mushaf_short_name = self.request.query_params.get('mushaf')
        if self.action == 'list' and not mushaf_short_name:
            raise serializers.ValidationError({'mushaf': 'This query parameter is required.'})
        if mushaf_short_name:
            queryset = queryset.filter(mushaf__short_name=mushaf_short_name)
        return queryset.order_by('number')

    def perform_create(self, serializer):
        # Get the last surah number
        last_surah = Surah.objects.order_by('-number').first()
        next_number = 1 if last_surah is None else last_surah.number + 1

        # Save the surah with the next number
        serializer.save(creator=self.request.user, number=next_number)

@extend_schema_view(
    list=extend_schema(
        summary="List all Ayahs (Quran verses)",
        parameters=[
            OpenApiParameter("surah_uuid", OpenApiTypes.UUID, OpenApiParameter.QUERY)
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Ayah by UUID"),
    create=extend_schema(summary="Create a new Ayah record"),
    update=extend_schema(summary="Update an existing Ayah record"),
    partial_update=extend_schema(summary="Partially update an Ayah record"),
    destroy=extend_schema(summary="Delete an Ayah record")
)
class AyahViewSet(viewsets.ModelViewSet):
    queryset = Ayah.objects.all().order_by('surah__number', 'number')
    serializer_class = AyahSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        core_permissions.IsCreatorOfParentOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
    ]

    def get_parent_for_permission(self, request):
        """
        For create requests, return the Surah object to check ownership.
        This is used by IsCreatorOrReadOnly permission.
        """
        surah_uuid = request.data.get('surah_uuid', None)
        if surah_uuid:
            return Surah.objects.filter(uuid=surah_uuid).first()
        return None

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "text"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    lookup_field = "uuid"

    def get_queryset(self):
        ayah_fields = [
            'uuid', 'surah', 'number', 'sajdah', 'is_bismillah', 'bismillah_text', 'creator'
        ]
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.select_related('surah', 'surah__mushaf').prefetch_related('words').only(*ayah_fields)
        else:
            queryset = queryset.select_related('surah').prefetch_related('words').only(*ayah_fields)
        surah_uuid = self.request.query_params.get('surah_uuid', None)
        if surah_uuid is not None:
            queryset = queryset.filter(surah__uuid=surah_uuid)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        text_format = self.request.query_params.get('text_format', 'text')
        # Validate format parameter
        if text_format not in ['text', 'word']:
            text_format = 'text'
        context['text_format'] = text_format
        return context

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AyahSerializerView
        if self.action == 'create':
            return AyahAddSerializer
        return AyahSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

@extend_schema_view(
    list=extend_schema(
        summary="List all Words in Ayahs",
        parameters=[
            OpenApiParameter(
                name="ayah_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Ayah to filter Words by."
            )
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Word by UUID"),
    create=extend_schema(
        summary="Create a new Word record",
        parameters=[
            OpenApiParameter(
                name="ayah_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Ayah to associate the new Word with (if ayah_id is not provided in the body)."
            )
        ]
    ),
    update=extend_schema(summary="Update an existing Word record"),
    partial_update=extend_schema(summary="Partially update a Word record"),
    destroy=extend_schema(summary="Delete a Word record")
)
class WordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Word objects (words within Ayahs).
    Allows filtering by Ayah and searching by word text.
    """
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        core_permissions.IsCreatorOfParentOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
    ]
    def get_parent_for_permission(self, request):
        """
        For create requests, return the Ayah object to check ownership.
        This is used by IsCreatorOrReadOnly permission.
        """
        ayah_uuid = request.data.get('ayah_uuid', None)
        if ayah_uuid:
            return Ayah.objects.filter(uuid=ayah_uuid).first()
        return None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    lookup_field = "uuid"
    
    def get_queryset(self):
        word_fields = [
            'uuid', 'ayah', 'text', 'creator'
        ]
        queryset = Word.objects.select_related('ayah').only(*word_fields)
        ayah_uuid = self.request.query_params.get('ayah_uuid', None)
        if ayah_uuid is not None:
            queryset = queryset.filter(ayah__uuid=ayah_uuid)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if not data.get('ayah_id'):
            ayah_uuid = request.query_params.get('ayah_uuid')
            if ayah_uuid:
                data['ayah_id'] = ayah_uuid
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

@extend_schema_view(
    list=extend_schema(
        summary="List all Quran Translations",
        parameters=[
            OpenApiParameter(
                name="mushaf",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Short name of the Mushaf to filter Translations by."
            ),
            OpenApiParameter(
                name="language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Language code to filter Translations by."
            )
        ],
        tags=["general", "translations"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific Translation by UUID",
        parameters=[
            OpenApiParameter(
                name="surah_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Surah to filter ayahs_translations by."
            )
        ],
        tags=["general", "translations"],
    ),
    create=extend_schema(summary="Create a new Translation record"),
    update=extend_schema(summary="Update an existing Translation record"),
    partial_update=extend_schema(summary="Partially update a Translation record"),
    destroy=extend_schema(summary="Delete a Translation record")
)
class TranslationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Translation objects (Quran translations).
    Supports filtering by Mushaf and language, and restricts editing of published translations.
    """
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions,
        core_permissions.LimitedFieldEditPermission
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"
    
    def get_queryset(self):
        translation_fields = [
            'uuid', 'mushaf', 'translator', 'language', 'release_date', 'source', 'status', 'creator'
        ]
        queryset = Translation.objects.select_related('mushaf', 'translator').only(*translation_fields)
        mushaf_short_name = self.request.query_params.get('mushaf')
        if self.action == 'list' and not mushaf_short_name:
            raise serializers.ValidationError({'mushaf': 'This query parameter is required.'})
        if mushaf_short_name:
            queryset = queryset.filter(mushaf__short_name=mushaf_short_name)
        language = self.request.query_params.get('language', None)
        if language is not None:
            queryset = queryset.filter(language=language)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            from .serializers import TranslationSerializer
            return TranslationSerializer
        from .serializers import TranslationListSerializer
        return TranslationListSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Allow admin users to edit even if published
        if instance.status == 'published' and not request.user.is_staff:
            return Response({'detail': 'Published Translation cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)
        status_value = request.data.get('status')
        # Only check if status is being set to pending_review
        if status_value == 'pending_review':
            # Count ayahs for this translation's mushaf
            ayah_count = Ayah.objects.filter(surah__mushaf=instance.mushaf).count()
            ayah_translation_count = AyahTranslation.objects.filter(translation=instance).count()
            if ayah_translation_count != ayah_count:
                return Response({
                    'detail': f'Translation is incomplete: {ayah_translation_count} of {ayah_count} ayahs translated.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, partial=partial, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary", "description": "JSON file containing the Translation data"}
                },
                "required": ["file"]
            }
        },
        summary="Import a Translation from a JSON file upload"
    )
    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser, FormParser])
    def import_translation(self, request):
        """
        Import a Translation from an uploaded JSON file.
        Expects a file field in the multipart/form-data.
        """
        TRANSLATION_UPLOAD_MAX_SIZE = 30 * 1024 * 1024

        file = request.FILES.get('file')
        if file.size > TRANSLATION_UPLOAD_MAX_SIZE:
            return Response(
                {'error': f'File size exceeds the maximum allowed for translation import ({TRANSLATION_UPLOAD_MAX_SIZE} bytes, got {file.size} bytes).'},
                status=400
            )
        if not file:
            return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        # Check file extension
        if not file.name.lower().endswith('.json'):
            return Response({'detail': 'Only JSON files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            translation_data = json.load(file)
            user = request.user
            from quran.tasks import import_translation_task
            import_translation_task.delay(translation_data, user.id)
            return Response({'detail': 'Translation import started. You will be notified when it is complete.'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        surah_uuid = request.query_params.get('surah_uuid')
        if not surah_uuid:
            return Response({'detail': 'surah_uuid query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        ayahs_translations_qs = (
            instance.ayah_translations
            .select_related('ayah', 'ayah__surah')
            .filter(ayah__surah__uuid=surah_uuid)
            .order_by('ayah__number')
        )

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(ayahs_translations_qs, request)
        from .serializers import AyahTranslationNestedSerializer
        if page is not None:
            ayahs_translations = AyahTranslationNestedSerializer(page, many=True).data
            data['ayahs'] = ayahs_translations
            return paginator.get_paginated_response(data)

        ayahs_translations = AyahTranslationNestedSerializer(ayahs_translations_qs, many=True).data
        data['ayahs'] = ayahs_translations
        return Response(data)

    @extend_schema(
        summary="List all AyahTranslations for this Translation",
        description=(
            "Returns a paginated list of all AyahTranslation objects for the given Translation UUID. "
            "Optionally filter by surah_uuid (query param)."
        ),
        parameters=[
            OpenApiParameter(
                name="surah_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Surah to filter AyahTranslations by."
            )
        ],
        responses={200: AyahTranslationSerializer(many=True)}
    )
    @action(detail=True, methods=["get"], url_path="ayahs")
    def ayahs(self, request, *args, **kwargs):
        """
        List all AyahTranslation objects for this Translation.
        Optional query param: surah_uuid to filter by Surah.
        For the returned list, only the first ayah should have its 'bismillah' value from DB; the rest should be null.
        """
        translation = self.get_object()
        ayah_translations = translation.ayah_translations.select_related('ayah', 'ayah__surah').order_by('ayah__number')
        surah_uuid = request.query_params.get('surah_uuid')
        if surah_uuid:
            ayah_translations = ayah_translations.filter(ayah__surah__uuid=surah_uuid)
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(ayah_translations, request)
        from .serializers import AyahTranslationNestedSerializer
        def process_bismillah(data):
            # Only the first ayah keeps its bismillah, the rest are set to None
            found_first = False
            for item in data:
                if not found_first:
                    found_first = True
                else:
                    item['bismillah'] = None
            return data
        if page is not None:
            serializer = AyahTranslationNestedSerializer(page, many=True)
            processed = process_bismillah(serializer.data)
            return paginator.get_paginated_response(processed)
        serializer = AyahTranslationNestedSerializer(ayah_translations, many=True)
        processed = process_bismillah(serializer.data)
        return Response(processed)
    @extend_schema(
        summary="Create or update (upsert) a specific AyahTranslation",
        description=(
            "Provide the ayah's UUID in the URL path and the translation's UUID as the primary resource path. "
            "Body requires only `text` (and optional `bismillah`). If an AyahTranslation already exists it will be "
            "updated, otherwise it will be created."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "bismillah": {"type": "boolean"}
                },
                "required": ["text"]
            }
        },
        methods=["PUT", "POST"],
        responses={201: AyahTranslationSerializer, 200: AyahTranslationSerializer}
    )
    @action(detail=True, methods=["put", "post"], url_path="ayahs/(?P<ayah_uuid>[^/.]+)")
    def modify_ayah_translation(self, request, *args, **kwargs):
        """
        Upsert endpoint at
            /translations/{translation_uuid}/ayahs/{ayah_uuid}/

        * `translation_uuid` – taken from the main URL (handled by viewset)
        * `ayah_uuid` – path parameter captured by the regex in `url_path`

        Body parameters:
            text: str (required)
            bismillah: bool (optional)

        Returns the created/updated `AyahTranslation` representation.
        """
        from .serializers import AyahTranslationSerializer

        translation: Translation = self.get_object()
        ayah_uuid = kwargs.get("ayah_uuid")

        serializer = AyahTranslationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data.get('text')
        bismillah = serializer.validated_data.get('bismillah', None)

        # Perform update or create
        ayah_translation, created = AyahTranslation.objects.update_or_create(
            ayah__uuid=ayah_uuid,
            translation=translation,
            defaults={
                'text': text,
                'bismillah': bismillah,
                'creator': request.user
            }
        )

        output_serializer = AyahTranslationSerializer(ayah_translation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@extend_schema_view(
    list=extend_schema(
        summary="List all Recitations (audio recordings)",
        parameters=[
            OpenApiParameter(
                name="mushaf",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Short name of the Mushaf to filter Recitations by."
            ),
            OpenApiParameter(
                name="reciter_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Reciter to filter Recitations by."
            )
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Recitation by UUID"),
    create=extend_schema(summary="Create a new Recitation record"),
    update=extend_schema(summary="Update an existing Recitation record"),
    partial_update=extend_schema(summary="Partially update a Recitation record"),
    destroy=extend_schema(summary="Delete a Recitation record")
)
class RecitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Recitation objects (audio recitations of the Quran).
    Supports filtering by Mushaf and reciter, and restricts editing of published recitations.
    """
    queryset = Recitation.objects.all()
    serializer_class = RecitationSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions,
        core_permissions.LimitedFieldEditPermission
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["recitation_date", "recitation_location", "recitation_type"]
    ordering_fields = ['created_at', 'duration', 'recitation_date']
    pagination_class = CustomPageNumberPagination
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"

    def get_queryset(self):
        recitation_fields = [
            'uuid', 'mushaf', 'reciter_account', 'recitation_date', 'recitation_location', 'duration', 'recitation_type', 'status', 'creator'
        ]
        queryset = Recitation.objects.select_related('mushaf', 'reciter_account').only(*recitation_fields)
        # Filter by mushaf if provided
        mushaf_short_name = self.request.query_params.get('mushaf')
        if self.action == 'list' and not mushaf_short_name:
            raise serializers.ValidationError({'mushaf': 'This query parameter is required.'})
        if mushaf_short_name:
            queryset = queryset.filter(mushaf__short_name=mushaf_short_name)
        # Filter by reciter if provided
        reciter_uuid = self.request.query_params.get('reciter_uuid', None)
        if reciter_uuid is not None:
            queryset = queryset.filter(reciter_account__uuid=reciter_uuid)
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('recitation_surahs__timestamps')
        return queryset

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Allow admin users to edit even if published
        if instance.status == 'published' and not request.user.is_staff:
            return Response({'detail': 'Published Recitation cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)
        status_value = request.data.get('status')
        if status_value == 'pending_review':
            # Count ayahs for this recitation's mushaf
            ayah_count = Ayah.objects.filter(surah__mushaf=instance.mushaf).count()
            ayah_translation_count = AyahTranslation.objects.filter(translation__mushaf=instance.mushaf).count()
            if ayah_translation_count != ayah_count:
                return Response({
                    'detail': f'Recitation is incomplete: {ayah_translation_count} of {ayah_count} ayahs translated.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, partial=partial, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    # ---- New Action: Upload Surah audio & timestamps ----
    @extend_schema(
        summary="Upload a surah audio file and optional word-level timestamps for a Recitation",
        description=(
            "Accepts a multipart/form-data request with the following parts:\n"
            "• file: The MP3 audio file for the surah.\n"
            "• word_timestamps (optional): JSON string array of objects with start, end, word_uuid."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                    "word_timestamps": {"type": "string", "description": "JSON list, optional"},
                },
                "required": ["file"],
            }
        },
        responses={201: OpenApiTypes.OBJECT},
        methods=["POST"],
    )
    @action(detail=True, methods=["post"], url_path="upload/(?P<surah_uuid>[^/.]+)", parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, *args, **kwargs):
        """Attach a surah-level audio file (and optional timestamps) to an existing Recitation."""
        import uuid as _uuid
        from django.db import transaction
        recitation: Recitation = self.get_object()

        # Check permissions against this object manually since we're in a detail=False action
        self.check_object_permissions(request, recitation)

        file_obj = request.FILES.get("file")
        surah_uuid = kwargs.get("surah_uuid")
        word_ts_raw = request.data.get("word_timestamps")

        if not file_obj:
            return Response({"file": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not surah_uuid:
            return Response({"surah_uuid": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate surah
        try:
            surah = Surah.objects.get(uuid=surah_uuid)
        except Surah.DoesNotExist:
            return Response({"detail": "Surah not found."}, status=status.HTTP_404_NOT_FOUND)

        # Basic permission: surah must belong to the same mushaf as the recitation
        if surah.mushaf_id != recitation.mushaf_id:
            return Response({"detail": "Surah does not belong to the same Mushaf as the recitation."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse word timestamps (if provided)
        word_timestamps = None
        if word_ts_raw:
            try:
                word_timestamps = json.loads(word_ts_raw)
                if not isinstance(word_timestamps, list):
                    raise ValueError
            except ValueError:
                return Response({"word_timestamps": "Invalid JSON – expected list."}, status=status.HTTP_400_BAD_REQUEST)

        # Upload file to S3 and create file record
        from core.utils import upload_mp3_to_s3
        try:
            new_file = upload_mp3_to_s3(file_obj, request.user, folder="recitations")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():

            # Create / get RecitationSurah
            recitation_surah, _ = RecitationSurah.objects.get_or_create(
                recitation=recitation,
                surah=surah,
                defaults={"file": new_file},
            )
            # If it already existed but had no file, attach
            if not recitation_surah.file_id:
                recitation_surah.file = new_file
                recitation_surah.save(update_fields=["file"])

            # Create timestamps if any
            if word_timestamps:
                from quran.models import Word
                from datetime import datetime

                ts_objs = []
                for ts in word_timestamps:
                    try:
                        start_time = datetime.strptime(ts["start"], "%H:%M:%S.%f")
                        end_time = (
                            datetime.strptime(ts["end"], "%H:%M:%S.%f") if ts.get("end") else None
                        )
                        word = None
                        if ts.get("word_uuid"):
                            word = Word.objects.filter(uuid=ts["word_uuid"]).first()
                        ts_objs.append(
                            RecitationSurahTimestamp(
                                recitation_surah=recitation_surah,
                                start_time=start_time,
                                end_time=end_time,
                                word=word,
                            )
                        )
                    except Exception:
                        continue
                if ts_objs:
                    RecitationSurahTimestamp.objects.bulk_create(ts_objs)

            # If no timestamps were provided, kick off forced-alignment generation
            if not word_timestamps:
                # Ensure the main recitation has an audio file reference for the task
                # No need to attach file to Recitation; file is stored on RecitationSurah.

                from quran.tasks import generate_recitation_surah_timestamps_task
                transaction.on_commit(lambda: generate_recitation_surah_timestamps_task.delay(
                    recitation, 
                    surah, 
                    new_file
                ))

        return Response({"detail": "Upload processed successfully."}, status=status.HTTP_201_CREATED)
