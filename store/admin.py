from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.db.models import Sum, Prefetch
from django.db import models
from django import forms
from django.db import IntegrityError

# from .forms import ColorValidation

from .models import Category, Customer, Discount, Mobile, Comment, Variety, Color, Image

@admin.register(Comment)
class CommentAdmmin(admin.ModelAdmin):
    list_display = ['id', 'short_title', 'owner', 'status', 'datetime_created']
    readonly_fields = ['owner', 'title', 'body']
    list_editable = ['status']
    exclude = ['content_type', 'object_id']


    @admin.display(ordering='title', description='title')
    def short_title(self, comment):
        return comment.title[:50]

    def get_model_perms(self, request):
        """
        Hide comments from list of store app
        """
        return {}

    def has_add_permission(self, request, obj=None):
        """
        Disable add comments from admin panel
        """
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent_category', 'is_sub']
    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title', ]
    }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sub_category')

    def parent_category(self, category):
        return category.sub_category


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'display_color']
    search_fields = ['name', 'code']

    @admin.display(description='#Colors')
    def display_color(self, color):
        """
        Display colored circles with html format
        opposite of each color name.
        """
        colored_circles = format_html(
                            f'<div style="display: flex; align-items: center;">'
                            f'<div style="margin-top: 2px; width: 20px; height:'
                            f'20px;border-radius: 50%; background-color: {color.code};'
                            f'border: 2px solid #B9B9B9; margin-right:5px; display:'
                            f'inline-block; text-align: center; line-height: 20px;"></div>'
                            ) 

        return format_html(colored_circles)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['discount', 'description']
    search_fields = ['discount']


class VarietyInline(GenericTabularInline):
    # form = ColorValidation
    model = Variety
    fields = ['color', 'inventory', 'unit_price']
    extra = 0
    min_num = 1

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                form.add_error('color', 'This color already exists for the product.')
            else:
                raise

    # TODO improve color querysets


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
        


@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = [
                    'id', 'name', 'category',
                    'mobile_variety','total_inventory',
                    'available', 'datetime_created',
                    'num_of_comments'
                    ]
    list_per_page = 10
    list_filter = [InventoryFilter, 'datetime_created', 'available']
    search_fields = ['name', 'category__title']
    autocomplete_fields = ['category', 'discount']
    show_facets = admin.ShowFacets.NEVER
    inlines = [VarietyInline, ImageInline,]
    actions = ['make_unavailable', 'make_available']
    prepopulated_fields = {
        'slug': ['name', ]
    }

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 30})},
    }

    def get_queryset(self, request):
        return Mobile.objects.select_related('category__sub_category') \
        .prefetch_related(
            Prefetch(
                'varieties',
                queryset=Variety.objects.select_related('color')
                )
        ).annotate(
            total_inventory=Sum('varieties__inventory'),
                    )
    
    @admin.display(description='# COMMENTS')
    def num_of_comments(self, obj):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({
                'object_id': obj.id
            })
        )
        return format_html('<a href="{}">{}</a>',url , 'SEE')


    @admin.display(description='#variety')
    def mobile_variety(self, mobile):
        """
        Display variety based on color and price.
        """
        colored_circles = [
            format_html(
                f'<div style="display: flex; align-items: center;">'
                f'<div style="margin-top: 2px; width: 20px; height:'
                f'20px; border-radius: 50%; background-color: {variety.color};'
                f'border: 2px solid #B9B9B9; margin-right:5px; display:'
                f'inline-block; text-align: center; line-height: 20px;"></div>'
                f'(Inventory: {variety.inventory}) (Price: ${variety.unit_price})</div>'
            ) for variety in mobile.varieties.all()
        ]
        return format_html(' '. join(colored_circles))

    
    @admin.display(ordering='total_inventory', description='# Total Inventory')
    def total_inventory(self, mobile):
        """
        Display total inventory of each mobile.
        """
        return mobile.total_inventory
    
    @admin.action(description='Make Unavailable')
    def make_unavailable(self, request, queryset):
        """
        A action method for unavailable mobiles.
        """
        mobile_names = list(queryset.values_list("name", flat=True))
        queryset.update(available=False)
        self.message_user(
            request,
            f'The mobile {" , ".join(mobile_names)} unavailabled'
        )

    @admin.action(description='Make Available')
    def make_available(self, request, queryset):
        """
        A action method for available mobiles.
        """
        mobile_names = list(queryset.values_list("name", flat=True))
        queryset.update(available=True)
        self.message_user(
            request,
            f'The mobile {" , ".join(mobile_names)} availabled'
        )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'email']
    list_per_page = 10
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name', 'user__email']

    def get_queryset(self, request):
        return Customer.objects.select_related('user')

    @admin.display(ordering='user__phone_number')
    def phone_number(self, customer):
        return customer.user.phone_number
    
    @admin.display(ordering='user__first_name')
    def first_name(self, customer):
        return customer.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self, customer):
        return customer.user.last_name
    
    @admin.display(ordering='user__email')
    def email(self, customer):
        return customer.user.email