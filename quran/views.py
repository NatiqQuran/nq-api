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
from core.pagination import CustomPageNumberPagination
from rest_framework.decorators import action
import json
from rest_framework.parsers import MultiPartParser, FormParser

@extend_schema_view(
    list=extend_schema(summary="List all Mushafs (Quranic manuscripts/editions)"),
    retrieve=extend_schema(summary="Retrieve a specific Mushaf by UUID"),
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
        """
        Import a Mushaf from an uploaded JSON file.
        Expects a file field in the multipart/form-data.
        """
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quran_data = json.load(file)
            user = request.user
            mushaf_data = quran_data["mushaf"]
            mushaf = Mushaf.objects.create(
                creator_id=user.id,
                name=mushaf_data["name"],
                short_name=mushaf_data["short_name"],
                source=mushaf_data["source"]
            )
            ayahs = []
            words = []
            surah_objs = []
            surah_number_to_obj = {}
            for surah_data in quran_data["surahs"]:
                surah = mushaf.surahs.create(
                    creator_id=user.id,
                    number=surah_data["number"],
                    name=surah_data["name"],
                    period=surah_data["period"]
                )
                surah_objs.append(surah)
                surah_number_to_obj[surah.number] = surah
                for ayah in surah_data["ayahs"]:
                    ayah_obj = Ayah(
                        creator_id=user.id,
                        surah=surah,
                        number=ayah["number"],
                        sajdah=ayah["sajdah"],
                        is_bismillah=ayah["is_bismillah"],
                        bismillah_text=ayah["bismillah_text"],
                    )
                    ayahs.append(ayah_obj)
                    for word in ayah["words"]:
                        words.append(Word(ayah=ayah_obj, text=word["text"], creator_id=user.id))
            Ayah.objects.bulk_create(ayahs)
            Word.objects.bulk_create(words)
            return Response({'detail': f'Mushaf {mushaf.name} imported successfully.'}, status=status.HTTP_201_CREATED)
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
                required=False,
                description="Short name of the Mushaf to filter Surahs by."
            )
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Surah by UUID"),
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
                name="mushaf_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Mushaf to filter Translations by."
            ),
            OpenApiParameter(
                name="language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Language code to filter Translations by."
            )
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Translation by UUID"),
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
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            translation_data = json.load(file)
            user = request.user
            # Get or create the user for the translator
            translator, _ = user.__class__.objects.get_or_create(username=translation_data["translator_username"])
            mushaf = Mushaf.objects.get(short_name=translation_data["mushaf"])
            translation = Translation.objects.create(
                creator_id=user.id,
                mushaf_id=mushaf.id,
                translator_id=translator.id,
                source=translation_data["source"],
                status="published",
                language=translation_data["language"],
            )
            ayah_translations = []
            first_ayah = translation_data["surahs"][0]["ayah_translations"][0]['text'] if translation_data["surahs"] and translation_data["surahs"][0]["ayah_translations"] else ""
            for surah in translation_data["surahs"]:
                for ayah in surah["ayah_translations"]:
                    ayah_translations.append(AyahTranslation(
                        creator_id=user.id,
                        translation_id=translation.id,
                        ayah_id=ayah["number"],
                        text=ayah["text"],
                        bismillah=first_ayah,
                    ))
            AyahTranslation.objects.bulk_create(ayah_translations)
            return Response({'detail': f'Translation {translation.id} imported successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        summary="List all Ayah Translations",
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    retrieve=extend_schema(summary="Retrieve a specific Ayah Translation by UUID"),
    create=extend_schema(
        summary="Create a new Ayah Translation record",
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    update=extend_schema(
        summary="Update an existing Ayah Translation record",
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    partial_update=extend_schema(
        summary="Partially update an Ayah Translation record",
        parameters=[
            OpenApiParameter(name='translation_uuid', description='Translation UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ayah_uuid', description='Ayah UUID', required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ]
    ),
    destroy=extend_schema(summary="Delete an Ayah Translation record")
)
class AyahTranslationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AyahTranslation objects (translations of individual Ayahs).
    Allows filtering by translation or ayah, and supports upsert on create.
    """
    queryset = AyahTranslation.objects.all()
    serializer_class = AyahTranslationSerializer
    permission_classes = [
        core_permissions.IsCreatorOrReadOnly,
        core_permissions.IsCreatorOfParentOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly | permissions.DjangoModelPermissions
    ]
    def get_parent_for_permission(self, request):
        """
        For create requests, return the Translation object to check ownership.
        This is used by IsCreatorOrReadOnly permission.
        """
        translation_uuid = request.data.get('translation_uuid', None)
        if translation_uuid:
            return Translation.objects.filter(uuid=translation_uuid).first()
        return None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text"]
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    lookup_field = "uuid"
    
    def get_queryset(self):
        ayah_translation_fields = [
            'uuid', 'translation', 'ayah', 'text', 'bismillah', 'creator'
        ]
        queryset = AyahTranslation.objects.select_related('translation', 'ayah').only(*ayah_translation_fields)
        translation_uuid = self.request.query_params.get('translation_uuid', None)
        ayah_uuid = self.request.query_params.get('ayah_uuid', None)
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

@extend_schema_view(
    list=extend_schema(
        summary="List all Recitations (audio recordings)",
        parameters=[
            OpenApiParameter(
                name="mushaf_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="UUID of the Mushaf to filter Recitations by."
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
            'uuid', 'mushaf', 'surah', 'reciter_account', 'recitation_date', 'recitation_location', 'duration', 'file', 'recitation_type', 'status', 'creator'
        ]
        queryset = Recitation.objects.select_related('mushaf', 'surah', 'reciter_account', 'file').only(*recitation_fields)
        # Filter by mushaf if provided
        mushaf_uuid = self.request.query_params.get('mushaf_uuid', None)
        if mushaf_uuid is not None:
            queryset = queryset.filter(mushaf__uuid=mushaf_uuid)
        # Filter by reciter if provided
        reciter_uuid = self.request.query_params.get('reciter_uuid', None)
        if reciter_uuid is not None:
            queryset = queryset.filter(reciter_account__uuid=reciter_uuid)
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('timestamps')
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
