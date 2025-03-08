from rest_framework import permissions, viewsets
from quran.models import Mushaf
from quran.serializers import MushafSerializer

class MushafViewSet(viewsets.ModelViewSet):
    queryset = Mushaf.objects.all().order_by('short_name')
    serializer_class = MushafSerializer
    permission_classes = [permissions.IsAuthenticated]