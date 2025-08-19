from rest_framework import permissions, viewsets, status, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

from core import permissions as core_permissions
from core.pagination import CustomLimitOffsetPagination
from quran.models import Mushaf, Surah
from quran.serializers import SurahSerializer, SurahDetailSerializer


@extend_schema_view(
	list=extend_schema(
		summary="List all Surahs (Quran chapters)",
		parameters=[
			OpenApiParameter(
				name="mushaf",
				type={"type": "string", "enum": ["hafs"]},
				location=OpenApiParameter.QUERY,
				required=True,
				description="Short name of the Mushaf to filter Surahs by. Common value: 'hafs'. Any string is accepted. (e.g. 'hafs', 'warsh', etc.)",
				examples=[OpenApiExample('hafs', value='hafs', summary='Most common')]
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
	queryset = Surah.objects.all().order_by('number')
	permission_classes = [
		core_permissions.IsCreatorOrReadOnly,
		core_permissions.IsCreatorOfParentOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
	]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["name"]
	ordering_fields = ['created_at']
	pagination_class = CustomLimitOffsetPagination
	lookup_field = "uuid"

	def get_parent_for_permission(self, request):
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
		last_surah = Surah.objects.order_by('-number').first()
		next_number = 1 if last_surah is None else last_surah.number + 1
		serializer.save(creator=self.request.user, number=next_number)
