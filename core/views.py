from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from rest_framework import viewsets, permissions, views
from .models import ErrorLog, Phrase, PhraseTranslation, File
from .serializers import (ErrorLogSerializer, PhraseModifySerializer,
                          PhraseSerializer,
                          PhraseTranslationSerializer)
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage
import uuid
from rest_framework.response import Response
import os
import magic
import hashlib
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers


@extend_schema_view(
    list=extend_schema(summary="List all error logs"),
    retrieve=extend_schema(summary="Retrieve a specific error log by ID"),
    create=extend_schema(summary="Create a new error log entry"),
    update=extend_schema(summary="Update an existing error log entry"),
    partial_update=extend_schema(summary="Partially update an error log entry"),
    destroy=extend_schema(summary="Delete an error log entry")
)
class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


@extend_schema_view(
    list=extend_schema(summary="List all phrases"),
    retrieve=extend_schema(summary="Retrieve a specific phrase by UUID"),
    create=extend_schema(summary="Create a new phrase"),
    update=extend_schema(summary="Update an existing phrase"),
    partial_update=extend_schema(summary="Partially update a phrase"),
    destroy=extend_schema(summary="Delete a phrase")
)
class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    lookup_field = "uuid"
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ["recitation_date", "recitation_location", "recitation_type"]
    # ordering_fields = ['created_at', 'duration', 'recitation_date']
    # pegination_class = None

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='language',
                location=OpenApiParameter.QUERY,
                type=str,
                required=True,
                description="Language code for the translation (required)."
            ),
        ],
        summary="Modify phrase translations",
        description="Modify phrase translations for a given language. The 'language' query parameter is required."
    )
    @action(detail=False, methods=['post'], serializer_class=PhraseModifySerializer)
    def modify(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        language = self.request.query_params.get('language')
        phrases = serializer.data["phrases"]

        for p in phrases:
            val = phrases[p]
            phrase = Phrase.objects.filter(phrase=p).first()
            if phrase is None:
                return HttpResponse(content=f"Phrase '{p}' not found!", status=404)

            phrase.translations.update_or_create(language=language, defaults={
                    "text": val, "creator_id": self.request.user.id,
                    }
                )
        return HttpResponse(content="Done", status=200)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List all phrase translations"),
    retrieve=extend_schema(summary="Retrieve a specific phrase translation by ID"),
    create=extend_schema(summary="Create a new phrase translation"),
    update=extend_schema(summary="Update an existing phrase translation"),
    partial_update=extend_schema(summary="Partially update a phrase translation"),
    destroy=extend_schema(summary="Delete a phrase translation")
)
class PhraseTranslationViewSet(viewsets.ModelViewSet):
    queryset = PhraseTranslation.objects.all()
    serializer_class = PhraseTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]


class Storage(S3Boto3Storage):
    """Storage object for s3
    
    Default location is uncategorized, and bucket name is
    from settings.

    Args:
        S3Boto3Storage (S3Boto3Storage): Storage
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    default_acl = 'public-read'
    file_overwrite = False
    location = 'uncategorized'


# Define allowed subjects and their file types
SUBJECTS = {
    "recitations": {
        "type": "mp3",
        "description": "Audio recitations of Quran"
    },
}

# Define MIME types for allowed file types
MIME_TYPES = {
    "mp3": ["audio/mp3", "audio/mpeg"],
}


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='subject',
            location=OpenApiParameter.QUERY,
            type=str,
            description='Subject of the file to be uploaded. Allowed subjects: recitations'
        ),
    ],
    request=OpenApiTypes.BINARY,
    operation_id='upload_file',
    summary='Upload a file to S3 with subject-based categorization',
    description='Uploads a file to S3 with public access, categorizing it based on the'
)
class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser, )
    permission_classes = [permissions.IsAuthenticated]

    def calculate_file_hash(self, file_obj):
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        # Read the file in chunks to handle large files efficiently
        for chunk in file_obj.chunks():
            sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def put(self, request, format=None):
        file_obj = request.FILES['file']
        original_filename = file_obj.name

        # Get subject from query parameters
        subject = request.query_params.get('subject')
        if not subject or subject not in SUBJECTS:
            return Response(
                {'error': f'Invalid or missing subject. Allowed subjects: {", ".join(SUBJECTS.keys())}'},
                status=400
            )

        # Get file extension from original filename
        _, ext = os.path.splitext(original_filename)
        ext = ext[1:].lower()  # Remove the dot and convert to lowercase

        # Validate file type
        if ext != SUBJECTS[subject]['type']:
            return Response(
                {'error': f'Invalid file type for {subject}. Expected {SUBJECTS[subject]["type"]}'},
                status=400
            )

        # Validate file content using magic
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(file_obj.read(1024))  # Read first 1024 bytes for MIME detection
        file_obj.seek(0)  # Reset file pointer to beginning

        # Check if the file's MIME type matches the expected type
        expected_mime_types = MIME_TYPES.get(ext, [])
        if not expected_mime_types or file_mime not in expected_mime_types:
            return Response(
                {'error': f'Invalid file content. File appears to be {file_mime} but should be {", ".join(expected_mime_types)}'},
                status=400
            )

        # Calculate file hash
        file_hash = self.calculate_file_hash(file_obj)
        file_obj.seek(0)  # Reset file pointer to beginning

        # Check for duplicate file
        existing_file = File.objects.filter(file_hash=file_hash).first()
        if existing_file:
            return Response({
                'uuid': existing_file.s3_uuid,
            })

        # Generate UUID for the file
        file_uuid = str(uuid.uuid4())

        # Create new filename with UUID
        new_filename = f"{file_uuid}.{ext}"

        # Save file to S3 with public access in subject-specific folder
        storage = Storage()
        storage.location = subject  # Set the folder based on subject
        storage.save(new_filename, file_obj)

        # Create file record in database
        File.objects.create(
            format=ext,
            size=file_obj.size,
            s3_uuid=file_uuid,
            upload_name=original_filename,
            file_hash=file_hash,
            uploader=request.user
        )

        return Response({
            'uuid': file_uuid,
        })


class UploadSubjectsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List allowed upload subjects",
        description="Returns a list of allowed subjects and their file types for file uploads.",
        responses=inline_serializer(
            name="UploadSubjectListResponse",
            many=True,
            fields={
                "subject": serializers.CharField(),
                "type": serializers.CharField(),
                "description": serializers.CharField(),
            }
        ),
        examples=[
            OpenApiExample(
                "Allowed upload subjects",
                value={
                    "subject": "recitations",
                    "type": "mp3",
                    "description": "Audio recitations of Quran"
                },
                summary="Allowed upload subjects",
                description="Example response showing allowed subjects and their file types.",
                response_only=True,
            )
        ]
    )
    def get(self, request, format=None):
        subjects_array = [
            {"subject": key, **value}
            for key, value in SUBJECTS.items()
        ]
        return Response(subjects_array)
