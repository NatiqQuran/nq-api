from django.db import models
from account.models import CustomUser
import os
import uuid

class ErrorLog(models.Model):
    error_name = models.CharField(max_length=256)
    status_code = models.IntegerField()
    message = models.TextField()
    detail = models.TextField(blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    request_token = models.CharField(max_length=64, blank=True, null=True)
    request_user_agent = models.TextField(blank=True, null=True)
    request_ipv4 = models.TextField()  # This field type is a guess.
    request_url = models.TextField(blank=True, null=True)
    request_controller = models.TextField(blank=True, null=True)
    request_action = models.TextField(blank=True, null=True)
    request_id = models.TextField(blank=True, null=True)
    request_body = models.BinaryField(blank=True, null=True)
    request_body_content_type = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Error: {self.error_name} - Status: {self.status_code} - Created at: {self.created_at} - Detail: {self.detail} - Account ID: {self.account_id} - Request token: {self.request_token} - Request user agent: {self.request_user_agent} - Request IPv4: {self.request_ipv4} - Request URL: {self.request_url} - Request controller: {self.request_controller} - Request action: {self.request_action} - Request ID: {self.request_id} - Request body: {self.request_body} - Request body content type: {self.request_body_content_type}"


class Phrase(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='phrases')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phrase = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.phrase

class PhraseTranslation(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='phrase_translation')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phrase = models.ForeignKey(Phrase, models.DO_NOTHING, related_name='translations')
    text = models.TextField()
    language = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text


def _get_random_filename(instance, filename):
    model_name = instance.__class__.__name__.lower()
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(model_name, new_filename)

class PublicDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=_get_random_filename)

class File(models.Model):
    format = models.CharField(max_length=10)  # mp3, jpg, etc.
    size = models.BigIntegerField()  # size in bytes
    s3_uuid = models.UUIDField()
    upload_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, null=True, blank=True)  # SHA256 hash is 64 characters
    deleted_time = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_files')
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_time = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['file_hash']),  # Add index for faster hash lookups
        ]

    def __str__(self):
        return f"{self.upload_name} ({self.format})"

    def get_absolute_url(self):
        from django.conf import settings
        return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/recitations/{self.s3_uuid}.{self.format}"
