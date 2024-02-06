# Generated by Django 5.0.1 on 2024-02-06 19:36

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]