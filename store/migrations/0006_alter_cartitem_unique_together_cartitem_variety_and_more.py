# Generated by Django 5.0.1 on 2024-02-25 11:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('store', '0005_alter_cartitem_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='variety',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='store.variety'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'object_id', 'content_type', 'variety')},
        ),
    ]
