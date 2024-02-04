from django.conf import settings
from django.db import models, IntegrityError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator 
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q

from colorfield.fields import ColorField



class Category(models.Model):
    sub_category = models.ForeignKey('self',
                                     verbose_name='category',
                                     on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     related_name='sub_cat'
                                    )
    is_sub = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'


    def __str__(self):    
        """
        Return full path category.
        """                       
        full_path = [self.title]             
        parent_name = self.sub_category
        while parent_name is not None:
            full_path.append(parent_name.title)
            parent_name = parent_name.sub_category
        return ' -> '.join(full_path[::-1])


class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
                                 Category, on_delete=models.PROTECT,
                                 related_name='products'
                                )
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    detatime_modified = models.DateTimeField(auto_now=True)
    discount = models.ManyToManyField(Discount, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    

class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na'
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='comment_owner')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=255)
    body = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=COMMENT_STATUS,
                              default=COMMENT_STATUS_WAITING)

    def __str__(self):
        return self.owner.phone_number
    

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = ColorField(default='FF0000', unique=True)

    def __str__(self):
        return self.name
    

class Variety(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    color = models.ForeignKey(
                              Color, on_delete=models.CASCADE,
                              related_name='colors'
                              )
    unit_price = models.IntegerField()
    inventory = models.PositiveIntegerField(
                                            default=1,
                                            validators=[MinValueValidator(1)]
                                            )
    def clean(self):
        color = self.color.id
        existing_color = Variety.objects.filter(object_id=self.object_id).values()

        print(color)
        print(existing_color)

        for items in existing_color:

            print(items['color_id'])
        
            if color == items['color_id']:
                raise ValidationError({'color':'This color already exists.'})
    
    
    def __str__(self):
        return ''


class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name


class Mobile(Product):
    networks = models.CharField(max_length=50)
    memory_card_support = models.CharField(max_length=50)
    sim_card_number = models.CharField(max_length=50)
    sim_description = models.CharField(max_length=50)
    backs_camera = models.CharField(max_length=50)
    internal_memory = models.CharField(max_length=50)
    ram = models.CharField(max_length=50)
    video_format_support = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    screen_technology = models.CharField(max_length=50)
    screen_size = models.CharField(max_length=50)
    picture_resolution = models.CharField(max_length=50)
    os_type = models.CharField(max_length=50)
    accessories = models.CharField(max_length=50)
    comments = GenericRelation(Comment)
    varieties = GenericRelation(Variety)
    images = GenericRelation(Image)
    
    def __str__(self):
        return self.name
    
    
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.phone_number
    

    
    
    