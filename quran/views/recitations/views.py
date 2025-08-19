from rest_framework import permissions, viewsets, status, filters, serializers
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiExample

from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Recitation, Surah, Ayah, AyahTranslation, RecitationSurah, RecitationSurahTimestamp
from quran.serializers import RecitationSerializer


@extend_schema_view(
	list=extend_schema(
		summary="List all Recitations (audio recordings)",
		parameters=[
			OpenApiParameter(
				name="mushaf",
				type={"type": "string", "enum": ["hafs"]},
				location=OpenApiParameter.QUERY,
				required=True,
				description="Short name of the Mushaf to filter Recitations by. Common value: 'hafs'. Any string is accepted. (e.g. 'hafs', 'warsh', etc.)",
				examples=[OpenApiExample('hafs', value='hafs', summary='Most common')]
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
	queryset = Recitation.objects.all()
	serializer_class = RecitationSerializer
	def get_serializer_class(self):
		if self.action == 'list':
			from quran.serializers import RecitationListSerializer
			return RecitationListSerializer
		return RecitationSerializer
	permission_classes = [
		core_permissions.IsCreatorOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions,
		core_permissions.LimitedFieldEditPermission
	]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["recitation_date", "recitation_location", "recitation_type"]
	ordering_fields = ['created_at', 'duration', 'recitation_date']
	pagination_class = CustomLimitOffsetPagination
	limited_fields = {"status": ["published"]}
	lookup_field = "uuid"

	def get_queryset(self):
		recitation_fields = ['uuid', 'mushaf', 'reciter_account', 'recitation_date', 'recitation_location', 'duration', 'recitation_type', 'status', 'creator']
		queryset = Recitation.objects.select_related('mushaf', 'reciter_account').only(*recitation_fields)
		mushaf_short_name = self.request.query_params.get('mushaf')
		if self.action == 'list' and not mushaf_short_name:
			raise serializers.ValidationError({'mushaf': 'This query parameter is required.'})
		if mushaf_short_name:
			queryset = queryset.filter(mushaf__short_name=mushaf_short_name)
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
		if instance.status == 'published' and not request.user.is_staff:
			return Response({'detail': 'Published Recitation cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)
		status_value = request.data.get('status')
		if status_value == 'pending_review':
			ayah_count = Ayah.objects.filter(surah__mushaf=instance.mushaf).count()
			ayah_translation_count = AyahTranslation.objects.filter(translation__mushaf=instance.mushaf).count()
			if ayah_translation_count != ayah_count:
				return Response({'detail': f'Recitation is incomplete: {ayah_translation_count} of {ayah_count} ayahs translated.'}, status=status.HTTP_400_BAD_REQUEST)
		return super().update(request, *args, partial=partial, **kwargs)

	def partial_update(self, request, *args, **kwargs):
		return self.update(request, *args, partial=True, **kwargs)

	@extend_schema(
		summary="Upload a surah audio file and optional word-level timestamps for a Recitation",
		description=("Accepts a multipart/form-data request with parts: file (mp3) and optional word_timestamps JSON list."),
		request={
			"multipart/form-data": {
				"type": "object",
				"properties": {"file": {"type": "string", "format": "binary"}, "word_timestamps": {"type": "string", "description": "JSON list, optional"}},
				"required": ["file"],
			},
		},
		responses={201: OpenApiTypes.OBJECT},
		methods=["POST"],
	)
	@action(detail=True, methods=["post"], url_path="upload/(?P<surah_uuid>[^/.]+)", parser_classes=[MultiPartParser, FormParser])
	def upload(self, request, *args, **kwargs):
		from core.utils import upload_mp3_to_s3
		from django.db import transaction
		recitation: Recitation = self.get_object()
		self.check_object_permissions(request, recitation)
		file_obj = request.FILES.get("file")
		surah_uuid = kwargs.get("surah_uuid")
		word_ts_raw = request.data.get("word_timestamps")
		if not file_obj:
			return Response({"file": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
		if not surah_uuid:
			return Response({"surah_uuid": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			surah = Surah.objects.get(uuid=surah_uuid)
		except Surah.DoesNotExist:
			return Response({"detail": "Surah not found."}, status=status.HTTP_404_NOT_FOUND)
		if surah.mushaf_id != recitation.mushaf_id:
			return Response({"detail": "Surah does not belong to the same Mushaf as the recitation."}, status=status.HTTP_400_BAD_REQUEST)
		word_timestamps = None
		if word_ts_raw:
			try:
				import json as _json
				word_timestamps = _json.loads(word_ts_raw)
				if not isinstance(word_timestamps, list):
					raise ValueError
			except ValueError:
				return Response({"word_timestamps": "Invalid JSON – expected list."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			new_file = upload_mp3_to_s3(file_obj, request.user, folder="recitations")
		except ValueError as e:
			return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
		with transaction.atomic():
			recitation_surah, _ = RecitationSurah.objects.get_or_create(
				recitation=recitation,
				surah=surah,
				defaults={"file": new_file},
			)
			if not recitation_surah.file_id:
				recitation_surah.file = new_file
				recitation_surah.save(update_fields=["file"])
			if word_timestamps:
				from quran.models import Word
				from datetime import datetime
				ts_objs = []
				for ts in word_timestamps:
					try:
						start_time = datetime.strptime(ts["start"], "%H:%M:%S.%f")
						end_time = (datetime.strptime(ts["end"], "%H:%M:%S.%f") if ts.get("end") else None)
						word = None
						if ts.get("word_uuid"):
							word = Word.objects.filter(uuid=ts["word_uuid"]).first()
						ts_objs.append(RecitationSurahTimestamp(recitation_surah=recitation_surah, start_time=start_time, end_time=end_time, word=word))
					except Exception:
						continue
				if ts_objs:
					RecitationSurahTimestamp.objects.bulk_create(ts_objs)
			if not word_timestamps:
				from quran.tasks import generate_recitation_surah_timestamps_task
				transaction.on_commit(lambda: generate_recitation_surah_timestamps_task.delay(recitation, surah, new_file))
		return Response({"detail": "Upload processed successfully."}, status=status.HTTP_201_CREATED)
