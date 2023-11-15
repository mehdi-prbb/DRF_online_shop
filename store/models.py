from django.db import models



class Category(models.Model):
    sub_category = models.ForeignKey('self',
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
        return self.title


class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    unit_price = models.IntegerField()
    inventory = models.IntegerField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    detatime_modified = models.DateTimeField(auto_now=True)
    discount = models.ManyToManyField(Discount, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    