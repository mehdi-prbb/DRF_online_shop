# Generated by Django 4.2.7 on 2024-01-08 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0004_mobilecomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobilecomment',
            name='owner',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='comment_owner', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
