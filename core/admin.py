from django.contrib import admin

from .models import ErrorLog, PhraseTranslation, Phrase

# Register your models here.
admin.site.register(ErrorLog)
admin.site.register(PhraseTranslation)
admin.site.register(Phrase)