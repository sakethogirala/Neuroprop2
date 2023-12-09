from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('name', 'email', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        ('Information', {'fields': ('name', 'email', 'password', 'date_joined')}),
        ('Permissions', {'fields': ('account_type', 'is_active', 'is_staff', 'groups', 'user_permissions')}),
        ('Misc', {'fields': ('activation_key',)}),
        
    )
    readonly_fields = ['date_joined']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'is_staff', 'is_active',)}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('pk',)

admin.site.register(User, CustomUserAdmin)

