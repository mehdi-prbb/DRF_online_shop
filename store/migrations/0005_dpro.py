# Generated by Django 5.0.1 on 2024-05-16 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_category_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dpro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('attributes', models.JSONField()),
            ],
        ),
    ]
