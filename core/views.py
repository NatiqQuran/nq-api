from rest_framework import viewsets, permissions
from .models import ErrorLog, Phrase, PhraseTranslation
from .serializers import ErrorLogSerializer, PhraseSerializer, PhraseTranslationSerializer

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticated]

class PhraseTranslationViewSet(viewsets.ModelViewSet):
    queryset = PhraseTranslation.objects.all()
    serializer_class = PhraseTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]
