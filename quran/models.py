from django.db import models

class Mushaf(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    short_name = models.CharField(max_length=100, blank=True, default='')
    name = models.TextField()
    source = models.TextField()
