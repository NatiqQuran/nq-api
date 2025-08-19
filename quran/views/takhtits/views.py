from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

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
	retrieve=extend_schema(summary="Retrieve a specific Takhtit by UUID", tags=["general", "takhtits"]),
	create=extend_schema(
		summary="Create a new Takhtit record",
		description="Create a new Takhtit. Requires mushaf_uuid and account_uuid in the request body.",
		request={
			"application/json": {
				"type": "object",
				"properties": {
					"mushaf_uuid": {"type": "string", "format": "uuid", "description": "UUID of the mushaf to link."},
					"account_uuid": {"type": "string", "format": "uuid", "description": "UUID of the account to link."}
				},
				"required": ["mushaf_uuid", "account_uuid"]
			}
		}
	),
	update=extend_schema(summary="Update an existing Takhtit record"),
	partial_update=extend_schema(summary="Partially update a Takhtit record"),
	destroy=extend_schema(summary="Delete a Takhtit record")
)
class TakhtitViewSet(viewsets.ModelViewSet):
	queryset = Takhtit.objects.all()
	serializer_class = TakhtitSerializer
	permission_classes = [
		core_permissions.IsCreatorOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
	]
	filterset_fields = ['mushaf', 'account', 'creator']
	search_fields = []
	ordering_fields = ['created_at', 'updated_at']
	ordering = ['-created_at']
	lookup_field = 'uuid'

	def perform_create(self, serializer):
		mushaf_uuid = self.request.data.get('mushaf_uuid')
		account_uuid = self.request.data.get('account_uuid')
		from quran.models import Mushaf
		from account.models import CustomUser
		mushaf = None
		account = None
		errors = {}
		if not mushaf_uuid:
			errors['mushaf_uuid'] = 'This field is required.'
		else:
			try:
				mushaf = Mushaf.objects.get(uuid=mushaf_uuid)
			except Mushaf.DoesNotExist:
				errors['mushaf_uuid'] = 'Mushaf not found.'
		if not account_uuid:
			errors['account_uuid'] = 'This field is required.'
		else:
			try:
				account = CustomUser.objects.get(uuid=account_uuid)
			except CustomUser.DoesNotExist:
				errors['account_uuid'] = 'Account not found.'
		if errors:
			from rest_framework.exceptions import ValidationError
			raise ValidationError(errors)
		serializer.save(creator=self.request.user, mushaf=mushaf, account=account)

	@extend_schema(
		summary="List all ayahs_breakers for this takhtit (ayahs map style)",
		description="Returns a flat list containing an entry for every ayah in this takhtit, with breaker info similar to the mushaf ayah_map action.",
		responses={200: AyahBreakersResponseSerializer(many=True)}
	)
	@action(detail=True, methods=["get"], url_path="ayahs_breakers")
	def ayahs_breakers(self, request, uuid=None):
		takhtit = self.get_object()
		ayah_ids = AyahBreaker.objects.filter(takhtit=takhtit).values_list('ayah_id', flat=True)
		ayah_qs = Ayah.objects.filter(id__in=ayah_ids).select_related("surah").order_by("surah__number", "number", "id")
		breakers_qs = (
			AyahBreaker.objects
			.filter(takhtit=takhtit, ayah__in=ayah_qs)
			.select_related("ayah", "ayah__surah")
			.order_by("ayah__surah__number", "ayah__number")
		)
		from collections import defaultdict
		breakers_by_ayah = defaultdict(list)
		for br in breakers_qs:
			breakers_by_ayah[br.ayah_id].append(br.type.lower())
		counters = {k: 0 for k in ["juz", "hizb", "ruku", "page", "rub", "manzil"]}
		data = []
		for ayah in ayah_qs:
			for br_type in breakers_by_ayah.get(ayah.id, []):
				key = br_type.split()[0]
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
				"rub": counters["rub"] or None,
				"manzil": counters["manzil"] or None,
			})
		return Response(data)

	@extend_schema(
		summary="Add an ayahs_breaker to this takhtit",
		description="Add a new ayahs_breaker to this takhtit. Requires ayah_uuid in the request body.",
		request={
			"application/json": {
				"type": "object",
				"properties": {
					"ayah_uuid": {"type": "string", "format": "uuid", "description": "UUID of the ayah to link."},
					"type": {"type": "string", "description": "Breaker type (see AyahBreakerType)."}
				},
				"required": ["ayah_uuid", "type"]
			}
		},
		responses={201: AyahBreakerSerializer}
	)
	@ayahs_breakers.mapping.post
	def add_ayahs_breaker(self, request, uuid=None):
		takhtit = self.get_object()
		data = request.data.copy()
		ayah_uuid = data.pop('ayah_uuid', None)
		breaker_type = data.get('type')
		if not ayah_uuid:
			return Response({"detail": "ayah_uuid is required."}, status=status.HTTP_400_BAD_REQUEST)
		if not breaker_type:
			return Response({"detail": "type is required."}, status=status.HTTP_400_BAD_REQUEST)
		from quran.models import Ayah, AyahBreakerType
		valid_types = [choice[0] for choice in AyahBreakerType.choices]
		if breaker_type not in valid_types:
			return Response({"detail": f"Invalid type. Must be one of: {', '.join(valid_types)}."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			ayah = Ayah.objects.get(uuid=ayah_uuid)
		except Ayah.DoesNotExist:
			return Response({"detail": "Ayah not found."}, status=status.HTTP_404_NOT_FOUND)
		data['takhtit'] = takhtit.pk
		data['ayah'] = ayah.pk
		serializer = AyahBreakerSerializer(data=data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	@extend_schema(
		summary="Retrieve a specific ayahs_breaker for this takhtit",
		parameters=[
			OpenApiParameter(
				name="breaker_uuid",
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.PATH,
				required=True,
				description="UUID of the ayahs_breaker."
			)
		],
		responses={200: AyahBreakerSerializer, 404: OpenApiTypes.OBJECT}
	)
	@action(detail=True, methods=["get"], url_path="ayahs_breakers/(?P<breaker_uuid>[^/.]+)")
	def retrieve_ayahs_breaker(self, request, uuid=None, breaker_uuid=None):
		takhtit = self.get_object()
		breaker = AyahBreaker.objects.filter(takhtit=takhtit, uuid=breaker_uuid).first()
		if not breaker:
			return Response({"detail": "AyahBreaker not found."}, status=404)
		serializer = AyahBreakerSerializer(breaker)
		return Response(serializer.data)

	@extend_schema(
		summary="List all words_breakers for this takhtit (with line counters)",
		description="Returns a flat list containing an entry for every word with a breaker for this takhtit, with a line counter (incremented for each breaker).",
		responses={200: WordBreakersResponseSerializer(many=True)}
	)
	@action(detail=True, methods=["get"], url_path="words_breakers")
	def words_breakers(self, request, uuid=None):
		takhtit = self.get_object()
		from quran.models import WordBreaker, Word
		word_breakers = (
			WordBreaker.objects
			.filter(takhtit=takhtit)
			.select_related('word', 'word__ayah')
			.order_by('word__ayah__surah__number', 'word__ayah__number', 'word__id')
		)
		line_counter = 0
		data = []
		for wb in word_breakers:
			line_counter += 1
			data.append({"word_uuid": str(wb.word.uuid), "line": line_counter})
		return Response(data)

	@extend_schema(
		summary="Add a words_breaker to this takhtit",
		description="Add a new words_breaker to this takhtit. Requires word_uuid in the request body. Only type 'line' is allowed.",
		request={
			"application/json": {
				"type": "object",
				"properties": {"word_uuid": {"type": "string", "format": "uuid", "description": "UUID of the word to link."}, "type": {"type": "string", "description": "Breaker type (must be 'line')."}},
				"required": ["word_uuid", "type"]
			}
		},
		responses={201: WordBreakerDetailResponseSerializer}
	)
	@words_breakers.mapping.post
	def add_words_breaker(self, request, uuid=None):
		takhtit = self.get_object()
		data = request.data.copy()
		word_uuid = data.pop('word_uuid', None)
		breaker_type = data.get('type')
		if not word_uuid:
			return Response({"detail": "word_uuid is required."}, status=status.HTTP_400_BAD_REQUEST)
		if not breaker_type:
			return Response({"detail": "type is required."}, status=status.HTTP_400_BAD_REQUEST)
		if breaker_type != 'line':
			return Response({"detail": "Invalid type. Only 'line' is allowed for WordBreaker."}, status=status.HTTP_400_BAD_REQUEST)
		from quran.models import Word, WordBreaker
		try:
			word = Word.objects.get(uuid=word_uuid)
		except Word.DoesNotExist:
			return Response({"detail": "Word not found."}, status=status.HTTP_404_NOT_FOUND)
		WordBreaker.objects.create(creator=request.user, word=word, takhtit=takhtit, type='line')
		return Response({"word_uuid": str(word.uuid), "type": "line"}, status=status.HTTP_201_CREATED)

	@extend_schema(
		summary="Retrieve a specific words_breaker for this takhtit",
		parameters=[
			OpenApiParameter(
				name="breaker_uuid",
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.PATH,
				required=True,
				description="UUID of the words_breaker."
			)
		],
		responses={200: WordBreakerDetailResponseSerializer, 404: OpenApiTypes.OBJECT}
	)
	@action(detail=True, methods=["get"], url_path="words_breakers/(?P<breaker_uuid>[^/.]+)")
	def retrieve_words_breaker(self, request, uuid=None, breaker_uuid=None):
		from quran.models import WordBreaker
		takhtit = self.get_object()
		breaker = WordBreaker.objects.filter(takhtit=takhtit, uuid=breaker_uuid).first()
		if not breaker:
			return Response({"detail": "WordBreaker not found."}, status=404)
		return Response({"word_uuid": str(breaker.word.uuid), "type": breaker.type})

	@extend_schema(
		summary="Import Ayah Breakers for the specified Takhtit",
		description=("Accepts a JSON array of strings with the format '{surah}:{ayah}' that denote the ayah at which a new breaker (page by default) begins. Existing breakers whose names start with the provided breaker type (default: 'page') will be removed before importing the new ones."),
		request={
			"multipart/form-data": {
				"type": "object",
				"properties": {"file": {"type": "string", "format": "binary", "description": "Text/JSON file containing a list of breakers (e.g. ['2:1', '2:6'])."}},
				"required": ["file"]
			}
		},
		methods=["POST"],
		parameters=[OpenApiParameter(name="type", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Breaker type (e.g., page, juz, hizb, ruku). Defaults to 'page'.")],
		responses={201: OpenApiTypes.OBJECT},
	)
	@action(detail=True, methods=["post"], url_path="import", parser_classes=[MultiPartParser, FormParser])
	def import_breakers(self, request, pk=None):
		import json
		from quran.models import Ayah, AyahBreaker, AyahBreakerType, Surah, Takhtit
		takhtit = self.get_object()
		breaker_type = request.query_params.get('type', 'page')
		file = request.FILES.get('file')
		if not file:
			return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			data = json.load(file)
		except Exception as e:
			return Response({'detail': f'Invalid file: {e}'}, status=status.HTTP_400_BAD_REQUEST)
		if not isinstance(data, list):
			return Response({'detail': 'File must contain a list of breakers.'}, status=status.HTTP_400_BAD_REQUEST)
		AyahBreaker.objects.filter(takhtit=takhtit, type=breaker_type).delete()
		created = 0
		for item in data:
			try:
				surah_num, ayah_num = map(int, item.split(':'))
				surah = Surah.objects.get(number=surah_num, mushaf=takhtit.mushaf)
				ayah = Ayah.objects.get(surah=surah, number=ayah_num)
				AyahBreaker.objects.create(ayah=ayah, takhtit=takhtit, type=breaker_type, creator=request.user)
				created += 1
			except Exception:
				continue
		return Response({'created': created}, status=status.HTTP_201_CREATED)
