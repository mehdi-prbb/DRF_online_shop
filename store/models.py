from uuid import uuid4
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator

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
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
                                 Category,
                                 on_delete=models.PROTECT
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
    object_id = models.UUIDField(default=uuid4)
    content_object = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=255)
    body = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=COMMENT_STATUS,
                              default=COMMENT_STATUS_WAITING)


    def __str__(self):
        return self.content_object.name
    

class Variety(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid4)
    content_object = GenericForeignKey('content_type', 'object_id')
    color_name = models.CharField(max_length=50)
    color_code = ColorField()                     
    unit_price = models.IntegerField()
    inventory = models.PositiveIntegerField(
                                            default=1,
                                            validators=[MinValueValidator(1)]
                                            )
    
    def __str__(self):
        return f'{self.color_name} {self.content_object.name}-"id"({self.id})'


class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid4)
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


class Laptop(Product):
    cpu = models.CharField(max_length=255)
    ram = models.CharField(max_length=255)
    internal_memory = models.CharField(max_length=255)
    gpu = models.CharField(max_length=255)
    battery_type = models.CharField(max_length=255)
    weight = models.CharField(max_length=255)
    screen_size = models.CharField(max_length=255)
    screen_resolution = models.CharField(max_length=255)
    dimensions = models.CharField(max_length=255)
    os_type = models.CharField(max_length=255)
    connections = models.CharField(max_length=255)
    accessories = models.CharField(max_length=255)
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
    

class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    ORDER_STATUS = [
        (ORDER_STATUS_PAID,'Paid'),
        (ORDER_STATUS_UNPAID,'Unpaid'),
        (ORDER_STATUS_CANCELED,'Canceled'),
    ]

    order_code = models.UUIDField(primary_key=True, default=uuid4)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default=ORDER_STATUS_UNPAID)


    def __str__(self):
        return self.customer.user.phone_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.UUIDField(default=uuid4)
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveSmallIntegerField()
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name='order_item_vars')

    class Meta:
        unique_together = [['order', 'object_id', 'content_type', 'variety']]

    def __str__(self):
        return f'{self.id}'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    cartitems = GenericRelation('CartItem')

    def __str__(self):
        return f'Cart ID : {self.id}'
    
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid4)
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name='item_vars')


    class Meta:
        unique_together = [['cart', 'object_id', 'content_type', 'variety']]

    
    def __str__(self):
        return f'{self.id}'
    

    
    