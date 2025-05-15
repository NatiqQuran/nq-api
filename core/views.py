from rest_framework.parsers import FileUploadParser
from django.http import HttpResponse
from rest_framework import viewsets, permissions, views
from .models import ErrorLog, Phrase, PhraseTranslation
from .serializers import ErrorLogSerializer, PhraseModifySerializer, PhraseSerializer, PhraseTranslationSerializer
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage

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
    bucket_name = 'testtest222'

class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser, )

    def put(self, request, filename, format=None):
        file_obj = request.FILES['file']
        storage = Storage()
        storage.save(filename, file_obj)
        # do some stuff with uploaded file
        return HttpResponse(status=204)

