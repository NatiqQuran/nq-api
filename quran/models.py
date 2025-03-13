from django.db import models
from django.contrib.auth.models import User

class Mushaf(models.Model):
    creator= models.ForeignKey(User, on_delete=models.CASCADE, related_name='mushafs')
    short_name = models.CharField(max_length=100, blank=True, default='')
    name = models.TextField()
    source = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
