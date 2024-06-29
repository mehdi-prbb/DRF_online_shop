# Generated by Django 5.0.1 on 2024-05-27 20:08

import colorfield.fields
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.FloatField()),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sub', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('sub_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sub_cat', to='store.category', verbose_name='category')),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(default=uuid.uuid4)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('w', 'Waiting'), ('a', 'Approved'), ('na', 'Not Approved')], default='w', max_length=2)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CommentDislike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dislikes', to='store.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='store.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HeadPhone',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('detatime_modified', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(default=True)),
                ('form_factor', models.CharField(max_length=255)),
                ('power_supply', models.CharField(max_length=255)),
                ('connectivity_tec', models.CharField(max_length=255)),
                ('another_features', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.category')),
                ('discount', models.ManyToManyField(blank=True, to='store.discount')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(default=uuid.uuid4)),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='images/')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Laptop',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('detatime_modified', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(default=True)),
                ('cpu', models.CharField(max_length=255)),
                ('ram', models.CharField(max_length=255)),
                ('internal_memory', models.CharField(max_length=255)),
                ('gpu', models.CharField(max_length=255)),
                ('battery_type', models.CharField(max_length=255)),
                ('weight', models.CharField(max_length=255)),
                ('screen_size', models.CharField(max_length=255)),
                ('screen_resolution', models.CharField(max_length=255)),
                ('dimensions', models.CharField(max_length=255)),
                ('os_type', models.CharField(max_length=255)),
                ('connections', models.CharField(max_length=255)),
                ('accessories', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.category')),
                ('discount', models.ManyToManyField(blank=True, to='store.discount')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mobile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('detatime_modified', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(default=True)),
                ('networks', models.CharField(max_length=50)),
                ('memory_card_support', models.CharField(max_length=50)),
                ('sim_card_number', models.CharField(max_length=50)),
                ('sim_description', models.CharField(max_length=50)),
                ('backs_camera', models.CharField(max_length=50)),
                ('internal_memory', models.CharField(max_length=50)),
                ('ram', models.CharField(max_length=50)),
                ('video_format_support', models.CharField(max_length=50)),
                ('size', models.CharField(max_length=50)),
                ('screen_technology', models.CharField(max_length=50)),
                ('screen_size', models.CharField(max_length=50)),
                ('picture_resolution', models.CharField(max_length=50)),
                ('os_type', models.CharField(max_length=50)),
                ('accessories', models.CharField(max_length=50)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.category')),
                ('discount', models.ManyToManyField(blank=True, to='store.discount')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_code', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('p', 'Paid'), ('u', 'Unpaid'), ('c', 'Canceled')], default='u', max_length=1)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='store.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Variety',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(default=uuid.uuid4)),
                ('color_name', models.CharField(max_length=50)),
                ('color_code', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=25, samples=None)),
                ('unit_price', models.IntegerField()),
                ('inventory', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(default=uuid.uuid4)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='store.order')),
                ('variety', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_item_vars', to='store.variety')),
            ],
            options={
                'unique_together': {('order', 'object_id', 'content_type', 'variety')},
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(default=uuid.uuid4)),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.cart')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('variety', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_vars', to='store.variety')),
            ],
            options={
                'unique_together': {('cart', 'object_id', 'content_type', 'variety')},
            },
        ),
    ]
