from rest_framework import permissions, viewsets, status, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Surah, Ayah
from quran.serializers import AyahSerializer, AyahSerializerView, AyahAddSerializer


@extend_schema_view(
	list=extend_schema(
		summary="List all Ayahs (Quran verses)",
		parameters=[OpenApiParameter("surah_uuid", OpenApiTypes.UUID, OpenApiParameter.QUERY)]
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
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["number", "text"]
	ordering_fields = ['created_at']
	pagination_class = CustomLimitOffsetPagination
	lookup_field = "uuid"

	def get_parent_for_permission(self, request):
		surah_uuid = request.data.get('surah_uuid', None)
		if surah_uuid:
			return Surah.objects.filter(uuid=surah_uuid).first()
		return None

	def get_queryset(self):
		ayah_fields = ['uuid', 'surah', 'number', 'sajdah', 'is_bismillah', 'bismillah_text', 'creator']
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
