from rest_framework import permissions, viewsets, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view

from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Mushaf, Ayah, AyahTranslation
from quran.serializers import MushafSerializer

import json


@extend_schema_view(
	list=extend_schema(summary="List all Mushafs (Quranic manuscripts/editions)", tags=["general", "mushafs"]),
	retrieve=extend_schema(summary="Retrieve a specific Mushaf by UUID", tags=["general", "mushafs"]),
	create=extend_schema(summary="Create a new Mushaf record"),
	update=extend_schema(summary="Update an existing Mushaf record"),
	partial_update=extend_schema(summary="Partially update a Mushaf record"),
	destroy=extend_schema(summary="Delete a Mushaf record")
)
class MushafViewSet(viewsets.ModelViewSet):
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
	pagination_class = CustomLimitOffsetPagination
	limited_fields = {"status": ["published"]}
	lookup_field = "uuid"

	def get_queryset(self):
		if getattr(self, 'action', None) == 'list':
			return Mushaf.objects.only('uuid', 'short_name', 'name', 'source', 'status').order_by('short_name')
		return Mushaf.objects.all().order_by('short_name')

	def perform_create(self, serializer):
		serializer.save(creator=self.request.user)

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		if instance.status == 'published' and not request.user.is_staff:
			return Response({'detail': 'Published Mushaf cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)
		status_value = request.data.get('status')
		if status_value == 'pending_review':
			ayah_count = Ayah.objects.filter(surah__mushaf=instance).count()
			ayah_translation_count = AyahTranslation.objects.filter(translation__mushaf=instance).count()
			if ayah_translation_count != ayah_count:
				return Response({'detail': f'Mushaf is incomplete: {ayah_translation_count} of {ayah_count} ayahs translated.'}, status=status.HTTP_400_BAD_REQUEST)
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
			return Response({'error': f'File size exceeds the maximum allowed for mushaf import ({MUSHAF_UPLOAD_MAX_SIZE} bytes, got {file.size} bytes).'}, status=400)
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
