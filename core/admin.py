from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff')
    list_filter = ('is_staff',)
    readonly_fields = ('last_login',)

    fieldsets = (
        (None, {'fields':(
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
            )}),
        ('permissions', {'fields':(
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'groups',
            'user_permissions'
            )})
    )

    add_fieldsets = (
        (None, {'fields':(
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
            )}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        # This form is to restrict the access of admins
        # to enable superuser for themselves
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form

