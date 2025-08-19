from rest_framework import permissions, viewsets, status, filters, serializers
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Ayah, Word
from quran.serializers import WordSerializer


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
	queryset = Word.objects.all()
	serializer_class = WordSerializer
	permission_classes = [
		core_permissions.IsCreatorOrReadOnly,
		core_permissions.IsCreatorOfParentOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
	]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["text"]
	ordering_fields = ['created_at']
	pagination_class = CustomLimitOffsetPagination
	lookup_field = "uuid"

	def get_parent_for_permission(self, request):
		ayah_uuid = request.data.get('ayah_uuid', None)
		if ayah_uuid:
			return Ayah.objects.filter(uuid=ayah_uuid).first()
		return None

	def get_queryset(self):
		word_fields = ['uuid', 'ayah', 'text', 'creator']
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
