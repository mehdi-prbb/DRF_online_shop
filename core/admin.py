from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Profile


class ProfileInline(admin.TabularInline):
    """
    Defines an inline admin descriptor for Profile model.
    specifies the fields to be displayed and wich fields shoud be read-only.
    """
    model= Profile
    fields = ['ssn', 'phone_number', 'image']
    readonly_fields = ['image', 'ssn', 'phone_number']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the CustomUser model.
    Defines the display, filter, readonly, search, ordering, and form configuration.
    """
    list_display = ('email', 'is_staff')
    list_filter = ('is_staff',)
    readonly_fields = (
            'last_login','username',
            'first_name', 'last_name','email')
    inlines = [ProfileInline]
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields':(
            'username', 'first_name',
            'last_name', 'email', 'password',
            )}),
        ('permissions', {'fields':(
            'is_active', 'is_staff',
            'is_superuser', 'last_login',
            'groups', 'user_permissions'
            )})
    )

    add_fieldsets = (
        (None, {'fields':(
            'username', 'first_name',
            'last_name', 'email',
            'password1', 'password2'
            )}),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides the default get_form method to disable the 'is_superuser' field
        if the requesting user is not a superuser.
        """
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form
