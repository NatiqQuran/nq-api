from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from rest_framework import viewsets, permissions, views
from .models import ErrorLog, Phrase, PhraseTranslation, File
from .serializers import ErrorLogSerializer, PhraseModifySerializer, PhraseSerializer, PhraseTranslationSerializer
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage
import uuid
from rest_framework.response import Response
import os
import magic  # Add this import

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]

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
    bucket_name = 'natiq'
    default_acl = 'public-read'
    file_overwrite = False
    location = 'bruh'

# Define allowed folders and their file types
FOLDERS = {
    "recitations": {
        "type": "mp3",
        "description": "Audio recitations of Quran"
    },
    "translations": {
        "type": "pdf",
        "description": "Translation documents"
    },
    "tajweed": {
        "type": "pdf",
        "description": "Tajweed learning materials"
    }
}

# Define MIME types for allowed file types
MIME_TYPES = {
    "mp3": ["audio/mp3"],
    "pdf": ["application/pdf"]
}

class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser, )
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, format=None):
        file_obj = request.FILES['file']
        original_filename = file_obj.name
        
        # Get subject from query parameters
        subject = request.query_params.get('subject')
        if not subject or subject not in FOLDERS:
            return Response(
                {'error': f'Invalid or missing subject. Allowed subjects: {", ".join(FOLDERS.keys())}'},
                status=400
            )
        
        # Get file extension from original filename
        _, ext = os.path.splitext(original_filename)
        ext = ext[1:].lower()  # Remove the dot and convert to lowercase
        
        # Validate file type
        if ext != FOLDERS[subject]['type']:
            return Response(
                {'error': f'Invalid file type for {subject}. Expected {FOLDERS[subject]["type"]}'},
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
            uploader=request.user
        )
        
        return Response({'uuid': file_uuid})

