from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from rest_framework import viewsets, permissions, views, filters
from .models import ErrorLog, Phrase, PhraseTranslation, File
from .serializers import ErrorLogSerializer, PhraseModifySerializer, PhraseSerializer, PhraseTranslationSerializer
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage
import uuid
from rest_framework.response import Response
import os
import magic
import hashlib
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ["recitation_date", "recitation_location", "recitation_type"]
    # ordering_fields = ['created_at', 'duration', 'recitation_date']
    # pegination_class = None

    @action(detail=False, methods=['post'], serializer_class=PhraseModifySerializer)
    def modify(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        language = self.request.query_params.get('language')
        phrases = serializer.data["phrases"]

        for p in phrases:
            val = phrases[p]
            phrase = Phrase.objects.filter(phrase=p).first()
            if phrase == None:
                return HttpResponse(content=f"Phrase '{p}' not found!",status=404)

            phrase.translations.update_or_create(language=language, defaults={
                    "text": val, "creator_id": self.request.user.id,
                    }
                )
        return HttpResponse(content="Done",status=200)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        

class PhraseTranslationViewSet(viewsets.ModelViewSet):
    queryset = PhraseTranslation.objects.all()
    serializer_class = PhraseTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]

class Storage(S3Boto3Storage):
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
        file_record = File.objects.create(
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

    def get(self, request, format=None):
        subjects_array = [
            {"subject": key, **value}
            for key, value in SUBJECTS.items()
        ]
        return Response(subjects_array)

