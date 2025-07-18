# Generated by Django 5.1.7 on 2025-06-05 12:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_hash',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['file_hash'], name='core_file_file_ha_8fa9b7_idx'),
        ),
    ]
