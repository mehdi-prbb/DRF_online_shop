# Generated by Django 4.2.7 on 2024-01-01 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='full_name',
        ),
    ]
