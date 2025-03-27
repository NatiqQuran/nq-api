from django.db import models
from django.contrib.auth.models import User

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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phrases')
    phrase = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.phrase

class PhraseTranslation(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phrase_translation')
    phrase = models.ForeignKey(Phrase, models.DO_NOTHING, related_name='translations')
    text = models.TextField()
    language = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text

