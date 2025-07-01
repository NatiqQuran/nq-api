from rest_framework import permissions, viewsets, status, filters
from rest_framework.response import Response
from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation, Recitation
from quran.serializers import (
    AyahSerializerView, MushafSerializer, SurahSerializer, SurahDetailSerializer, AyahSerializer, 
    WordSerializer, TranslationSerializer, AyahTranslationSerializer, AyahAddSerializer, RecitationSerializer
)

from core import permissions as core_permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend

class MushafViewSet(viewsets.ModelViewSet):
    queryset = Mushaf.objects.all().order_by('short_name')
    serializer_class = MushafSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions, core_permissions.LimitedFieldEditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["short_name", "name", "source"]
    ordering_fields = ['created_at']
    pegination_class = None
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"
    
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

class SurahViewSet(viewsets.ModelViewSet):
    queryset = Surah.objects.all().order_by('number')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ['created_at']
    pegination_class = None
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurahDetailSerializer
        return SurahSerializer
    
    def get_queryset(self):
        queryset = Surah.objects.all()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('ayahs__words')
        mushaf_short_name = self.request.query_params.get('mushaf', None)
        if mushaf_short_name is not None:
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
        parameters=[
            OpenApiParameter("surah_uuid", OpenApiTypes.UUID, OpenApiParameter.QUERY)
        ]
    )
)
class AyahViewSet(viewsets.ModelViewSet):
    queryset = Ayah.objects.all().order_by('surah__number', 'number')
    serializer_class = AyahSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "text"]
    ordering_fields = ['created_at']
    pegination_class = None
    lookup_field = "uuid"

    def get_queryset(self):
        queryset = super().get_queryset()
        surah_uuid = self.request.query_params.get('surah_uuid', None)
        
        # Apply surah filter if provided
        if surah_uuid is not None:
            queryset = queryset.filter(surah__uuid=surah_uuid)
            
        # Always prefetch words since we need them for both formats
        return queryset.prefetch_related('words')

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

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pegination_class = None
    lookup_field = "uuid"
    
    def get_queryset(self):
        queryset = Word.objects.all()
        ayah_uuid = self.request.query_params.get('ayah_uuid', None)
        if ayah_uuid is not None:
            queryset = queryset.filter(ayah__uuid=ayah_uuid)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions, core_permissions.LimitedFieldEditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pegination_class = None
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"
    
    def get_queryset(self):
        queryset = Translation.objects.all()
        mushaf_uuid = self.request.query_params.get('mushaf_uuid', None)
        language = self.request.query_params.get('language', None)
        
        if mushaf_uuid is not None:
            queryset = queryset.filter(mushaf__uuid=mushaf_uuid)
        if language is not None:
            queryset = queryset.filter(language=language)
        
        return queryset

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

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    create=extend_schema(
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    partial_update=extend_schema(
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    update=extend_schema(
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    )
)
class AyahTranslationViewSet(viewsets.ModelViewSet):
    queryset = AyahTranslation.objects.all()
    serializer_class = AyahTranslationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pegination_class = None
    lookup_field = "uuid"
    
    def get_queryset(self):
        queryset = AyahTranslation.objects.all()
        
        # Get translation and ayah UUIDs from URL parameters
        translation_uuid = self.request.query_params.get('translation_uuid', None)
        ayah_uuid = self.request.query_params.get('ayah_uuid', None)
        
        # Apply filters if UUIDs are provided
        if translation_uuid:
            queryset = queryset.filter(translation__uuid=translation_uuid)
        if ayah_uuid:
            queryset = queryset.filter(ayah__uuid=ayah_uuid)

        return queryset

    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        translation_uuid = self.request.query_params.get('translation_uuid')
        ayah_uuid = self.request.query_params.get('ayah_uuid')
        AyahTranslation.objects.update_or_create(
            ayah__uuid=ayah_uuid, 
            translation__uuid=translation_uuid,
            creator_id=self.request.user.id, 
            defaults={
                'text': serializer.validated_data['text'],
            }
        )
        return Response(status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class RecitationViewSet(viewsets.ModelViewSet):
    queryset = Recitation.objects.all()
    serializer_class = RecitationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions, core_permissions.LimitedFieldEditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["recitation_date", "recitation_location", "recitation_type"]
    ordering_fields = ['created_at', 'duration', 'recitation_date']
    pegination_class = None
    limited_fields = {
        "status": ["published"]
    }
    lookup_field = "uuid"

    def get_queryset(self):
        queryset = Recitation.objects.all()
        # Filter by mushaf if provided
        mushaf_uuid = self.request.query_params.get('mushaf_uuid', None)
        if mushaf_uuid is not None:
            queryset = queryset.filter(mushaf__uuid=mushaf_uuid)
        # Filter by reciter if provided
        reciter_uuid = self.request.query_params.get('reciter_uuid', None)
        if reciter_uuid is not None:
            queryset = queryset.filter(reciter_account__uuid=reciter_uuid)
        return queryset

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
