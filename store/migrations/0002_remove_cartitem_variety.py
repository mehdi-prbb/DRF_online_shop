# Generated by Django 5.0.1 on 2024-02-12 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='variety',
        ),
    ]