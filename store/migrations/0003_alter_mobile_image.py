# Generated by Django 4.2.7 on 2023-12-04 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_color_code_alter_color_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobile',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mobile_images', to='store.image'),
        ),
    ]
