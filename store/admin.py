from django import forms
from django.db import models
from django.urls import reverse
from django.db.models import Sum
from django.contrib import admin
from django.utils.http import urlencode
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
                    Category, Customer, Discount,
                    Mobile, Comment, Variety, Laptop,
                    Image, Order, OrderItem,
                    Cart, CartItem, HeadPhone
                    )


@admin.register(Comment)
class CommentAdmmin(admin.ModelAdmin):
    list_display = [
                    'id', 'product_name', 'category',
                    'short_title', 'owner', 'status',
                    'datetime_created', 
                    'likes', 'dislikes'
                    ]
    readonly_fields = ['owner', 'title', 'body']
    list_editable = ['status']
    exclude = ['content_type', 'object_id']
    list_per_page = 10

    def get_queryset(self, request):
        return Comment.objects.prefetch_related(
            'content_object',
            'likes', 'dislikes',
            'content_type') \
            .select_related('content_type', 'owner')


    @admin.display(ordering='title', description='title')
    def short_title(self, comment):
        return comment.title[:50]
    
    @admin.display(description='product')
    def product_name(self, comment):
        return comment.content_object.name
    
    @admin.display(description='category')
    def category(self, comment):
        return comment.content_type.name
    
    @admin.display(description='likes')
    def likes(self, comment):
        return comment.likes.count()
    
    @admin.display(description='dislikes')
    def dislikes(self, comment):
        return comment.dislikes.count()


    def has_add_permission(self, request, obj=None):
        """
        Disable add comments from admin panel
        """
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent_category', 'is_sub']
    search_fields = ['title']
    list_per_page = 10
    prepopulated_fields = {
        'slug': ['title', ]
    }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sub_category')

    def parent_category(self, category):
        return category.sub_category


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['discount', 'description']
    search_fields = ['discount']
    list_per_page = 10


class VarietyInline(GenericTabularInline):
    model = Variety
    extra = 0
    min_num = 1

    def get_queryset(self, request):
        return Variety.objects.prefetch_related('content_object')
    

class ImageInline(GenericTabularInline):
    model = Image
    fields = ['name', 'image']
    extra = 0
    min_num = 1


class InventoryFilter(admin.SimpleListFilter):
    """
    Filter inventory by remaining quantity.
    """
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    MORE_THAN_10 = '>10'

    title = "Critical Inventory Status"
    parameter_name = 'total_inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'High'),
            (InventoryFilter.BETWEEN_3_AND_10, 'Medium'),
            (InventoryFilter.MORE_THAN_10, 'Ok'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(total_inventory__lt=3)
        if self.value() == InventoryFilter.BETWEEN_3_AND_10:
            return queryset.filter(total_inventory__range=(3, 10))
        if self.value() == InventoryFilter.MORE_THAN_10:
            return queryset.filter(total_inventory__gt=10)
        

class ProductAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 30})},
    }

    @admin.display(description='id', ordering='id')
    def short_id(self, obj):
        return str(obj.id)[:7]

    
    @admin.display(description='# COMMENTS')
    def comments(self, obj):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({
                'object_id': obj.id
            })
        )
        return format_html('<a href="{}">{}</a>',url , 'SEE')


    @admin.display(description='#variety')
    def product_variety(self, obj):
        """
        Display variety based on color and price.
        """
        colored_circles = [
            format_html(
                f'<div style="display: flex; align-items: center;">'
                f'<div style="margin-top: 2px; width: 20px; height:'
                f'20px; border-radius: 50%; background-color: {variety.color_code};'
                f'border: 2px solid #B9B9B9; margin-right:5px; display:'
                f'inline-block; text-align: center; line-height: 20px;"></div>'
                f'(Inventory: {variety.inventory}) (Price: ${variety.unit_price})</div>'
            ) for variety in obj.varieties.all()
        ]
        return format_html(' '. join(colored_circles))

    
    @admin.display(ordering='total_inventory', description='# Total Inventory')
    def total_inventory(self, obj):
        """
        Display total inventory of each mobile.
        """
        return obj.total_inventory
    
    @admin.action(description='Make Unavailable')
    def make_unavailable(self, request, queryset):
        """
        A action method for unavailable mobiles.
        """
        obj_names = list(queryset.values_list("name", flat=True))
        queryset.update(available=False)
        self.message_user(
            request,
            f'The mobile {" , ".join(obj_names)} unavailabled'
        )

    @admin.action(description='Make Available')
    def make_available(self, request, queryset):
        """
        A action method for available mobiles.
        """
        obj_names = list(queryset.values_list("name", flat=True))
        queryset.update(available=True)
        self.message_user(
            request,
            f'The mobile {" , ".join(obj_names)} availabled'
        )


@admin.register(Mobile)
class MobileAdmin(ProductAdmin):
    list_display = [
                    'short_id', 'name', 'category',
                    'product_variety','total_inventory',
                    'available', 'datetime_created',
                    'comments'
                    ]
    readonly_fields = ['id']
    list_display_links = ['short_id', 'name']
    list_per_page = 10
    ordering = ['-datetime_created']
    list_filter = [InventoryFilter, 'datetime_created', 'available']
    search_fields = ['name', 'category__title']
    autocomplete_fields = ['category', 'discount']
    inlines = [VarietyInline, ImageInline,]
    actions = ['make_unavailable', 'make_available']
    show_facets = admin.ShowFacets.NEVER
    prepopulated_fields = {
        'slug': ['name', ]
    }

    def get_queryset(self, request):
        return Mobile.objects.select_related('category__sub_category') \
        .prefetch_related(
            'varieties',
        ).annotate(
            total_inventory=Sum('varieties__inventory'),
                    )


@admin.register(Laptop)
class LaptopAdmin(ProductAdmin):
    list_display = [
                    'short_id', 'name', 'category',
                    'product_variety','total_inventory',
                    'available', 'datetime_created',
                    'comments'
                    ]
    readonly_fields = ['id']
    list_display_links = ['short_id', 'name']
    list_per_page = 10
    list_filter = [InventoryFilter, 'datetime_created', 'available']
    search_fields = ['name', 'category__title']
    autocomplete_fields = ['category', 'discount']
    inlines = [VarietyInline, ImageInline,]
    actions = ['make_unavailable', 'make_available']
    show_facets = admin.ShowFacets.NEVER
    prepopulated_fields = {
        'slug': ['name', ]
    }

    def get_queryset(self, request):
        return Laptop.objects.select_related('category__sub_category') \
        .prefetch_related(
            'varieties',
        ).annotate(
            total_inventory=Sum('varieties__inventory'),
                    )
    

@admin.register(HeadPhone)
class HeadPhoneAdmin(ProductAdmin):
    list_display = [
                    'short_id', 'name', 'category',
                    'product_variety','total_inventory',
                    'available', 'datetime_created',
                    'comments'
                    ]
    readonly_fields = ['id']
    list_display_links = ['short_id', 'name']
    list_per_page = 10
    list_filter = [InventoryFilter, 'datetime_created', 'available']
    search_fields = ['name', 'category__title']
    autocomplete_fields = ['category', 'discount']
    inlines = [VarietyInline, ImageInline,]
    actions = ['make_unavailable', 'make_available']
    show_facets = admin.ShowFacets.NEVER
    prepopulated_fields = {
        'slug': ['name', ]
    }

    def get_queryset(self, request):
        return HeadPhone.objects.select_related('category__sub_category') \
        .prefetch_related(
            'varieties',
        ).annotate(
            total_inventory=Sum('varieties__inventory'),
                    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user',
                'username',
                'first_name',
                'last_name',
                'ssn',
                'phone_number'
                ]
    readonly_fields = ['user',
                'first_name', 'last_name',
                'ssn','phone_number']
    list_per_page = 10
    search_fields = [
                'user__first_name',
                'user__last_name', 'user__email',
                'user__profiles__phone_number',
                'user__profiles__ssn'
                ]

    def get_queryset(self, request):
        return Customer.objects.select_related('user__profiles')
    
    @admin.display(ordering='user__username')
    def username(self, customer):
        return customer.user.username
    
    @admin.display(ordering='user__first_name')
    def first_name(self, customer):
        return customer.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self, customer):
        return customer.user.last_name
    
    @admin.display(ordering='user__email')
    def email(self, customer):
        return customer.user.email
    
    @admin.display(ordering='user__profiles__ssn')
    def ssn(self, customer):
        return customer.user.profiles.ssn

    @admin.display(ordering='user__profiles__phone_number')
    def phone_number(self, customer):
        return customer.user.profiles.phone_number


class OrderAndCartProductDetails(admin.TabularInline):
    fields = [
        'product_type', 'product_name', 'product_color',
        'product_unit_price', 'quantity', 'items_total_price'
        ]
    readonly_fields = [
        'product_type', 'product_name',
        'product_color', 'product_unit_price',
        'quantity', 'items_total_price'
        ]
    max_num = 0

    def product_type(self, item):
        return f'{item.content_type.name}'
    product_type.short_description = 'Product type'

    def product_name(self, item):
        return f'{item.content_object.name}'
    product_name.short_description = 'Product name'

    def product_color(self, item):
        return f'{item.variety.color_name}'
    product_color.short_description = 'Product color'

    def product_unit_price(self, item):
        return f'{item.variety.unit_price}'
    product_unit_price.short_description = 'Product unit price'

    def items_total_price(self, item):
        return item.quantity * item.variety.unit_price
    items_total_price.short_description = 'Items total price'

class CartItemInline(OrderAndCartProductDetails):
    """
    Display items in cart.
    """
    model = CartItem

    def get_queryset(self, request):
        return CartItem.objects.prefetch_related(
            'content_object',
            'content_type',
            'variety')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Display cart in admin panel.
    """
    list_display = ['id', 'created_at']
    fields = ['cart_total_price']
    readonly_fields = ['cart_total_price']
    inlines = [CartItemInline]

    def cart_total_price(self, cart):
        """
        Calcute cart items total price.
        """
        return sum([item.quantity * item.variety.unit_price for item in cart.items.all()])


class OrderItemInline(OrderAndCartProductDetails):
    model = OrderItem
   
    def get_queryset(self, request):
        return OrderItem.objects.prefetch_related(
                            'content_type',
                            'content_object',
                            'variety'
                            )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'customer', 'status', 'datetime_created']
    list_display_links = ['order_code', 'customer']
    fields = ['status', 'order_total_price']
    readonly_fields = ['order_total_price']
    list_per_page = 10
    list_editable = ['status']
    ordering = ['-datetime_created']
    search_fields = ['order_code', 'status', 'datetime_created']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return Order.objects.select_related('customer__user').prefetch_related('items__variety')

    
    def order_total_price(self, order):
        """
        Calcute order items total price.
        """
        return sum([item.quantity * item.variety.unit_price for item in order.items.all()])


