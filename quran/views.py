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
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class SurahViewSet(viewsets.ModelViewSet):
    queryset = Surah.objects.all().order_by('number')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ['created_at']
    pegination_class = None

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
            OpenApiParameter("surah_id", 
                    OpenApiTypes.NUMBER, 
                    OpenApiParameter.QUERY)
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

    def get_queryset(self):
        queryset = super().get_queryset()
        surah_id = self.request.query_params.get('surah_id', None)
        
        # Apply surah filter if provided
        if surah_id is not None:
            queryset = queryset.filter(surah_id=surah_id)
            
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
    
    def get_queryset(self):
        queryset = Word.objects.all()
        ayah_id = self.request.query_params.get('ayah_id', None)
        if ayah_id is not None:
            queryset = queryset.filter(ayah_id=ayah_id)
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
    
    def get_queryset(self):
        queryset = Translation.objects.all()
        mushaf = self.request.query_params.get('mushaf_id', None)
        language = self.request.query_params.get('language', None)
        
        if mushaf is not None:
            queryset = queryset.filter(mushaf__short_name=mushaf)
        if language is not None:
            queryset = queryset.filter(language=language)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class AyahTranslationViewSet(viewsets.ModelViewSet):
    queryset = AyahTranslation.objects.all()
    serializer_class = AyahTranslationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pegination_class = None
    
    def get_queryset(self):
        queryset = AyahTranslation.objects.all()
        
        # Get translation and ayah IDs from URL parameters
        translation_id = self.request.query_params.get('translation_id', None)
        ayah_id = self.request.query_params.get('ayah_id', None)
        
        # Apply filters if IDs are provided
        if translation_id:
            queryset = queryset.filter(translation_id=translation_id)
        if ayah_id:
            queryset = queryset.filter(ayah_id=ayah_id)

        return queryset

    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        translation_id = self.request.query_params.get('translation_id')
        ayah_id = self.request.query_params.get('ayah_id')
        AyahTranslation.objects.update_or_create(
            ayah_id=ayah_id, 
            translation_id=translation_id,
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

    def get_queryset(self):
        queryset = Recitation.objects.all()
        # Filter by mushaf if provided
        mushaf_id = self.request.query_params.get('mushaf_id', None)
        if mushaf_id is not None:
            queryset = queryset.filter(mushaf_id=mushaf_id)
        # Filter by reciter if provided
        reciter_id = self.request.query_params.get('reciter_id', None)
        if reciter_id is not None:
            queryset = queryset.filter(reciter_account_id=reciter_id)
        return queryset
