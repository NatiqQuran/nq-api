from rest_framework import permissions, viewsets
from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation
from quran.serializers import (
    MushafSerializer, SurahSerializer, AyahSerializer, 
    WordSerializer, TranslationSerializer, AyahTranslationSerializer
)

class MushafViewSet(viewsets.ModelViewSet):
    queryset = Mushaf.objects.all().order_by('short_name')
    serializer_class = MushafSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class SurahViewSet(viewsets.ModelViewSet):
    queryset = Surah.objects.all().order_by('number')
    serializer_class = SurahSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    
    def get_queryset(self):
        queryset = Surah.objects.all()
        mushaf_short_name = self.request.query_params.get('mushaf', None)
        if mushaf_short_name is not None:
            queryset = queryset.filter(mushaf__short_name=mushaf_short_name)
        return queryset.order_by('number')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class AyahViewSet(viewsets.ModelViewSet):
    queryset = Ayah.objects.all().order_by('surah__number', 'number')
    serializer_class = AyahSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        surah_id = self.request.query_params.get('surah', None)
        
        # Apply surah filter if provided
        if surah_id is not None:
            queryset = queryset.filter(surah_id=surah_id)
            
        # Always prefetch words since we need them for both formats
        return queryset.prefetch_related('words')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        format_param = self.request.query_params.get('format', 'text')
        # Validate format parameter
        if format_param not in ['text', 'word']:
            format_param = 'text'
        context['format'] = format_param
        return context

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    
    def get_queryset(self):
        queryset = Word.objects.all()
        ayah_id = self.request.query_params.get('ayah', None)
        if ayah_id is not None:
            queryset = queryset.filter(ayah_id=ayah_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    
    def get_queryset(self):
        queryset = Translation.objects.all()
        mushaf = self.request.query_params.get('mushaf', None)
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
    
    def get_queryset(self):
        queryset = AyahTranslation.objects.all()
        translation_id = self.request.query_params.get('translation', None)
        ayah_id = self.request.query_params.get('ayah', None)
        
        if translation_id is not None:
            queryset = queryset.filter(translation_id=translation_id)
        if ayah_id is not None:
            queryset = queryset.filter(ayah_id=ayah_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)