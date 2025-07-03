# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from events.models import Participation

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'location', 'birth_date', 'gender', 'phone_number', 'latitude', 'longitude', 'interests')
    list_filter = ('is_staff', 'is_active', 'location', 'gender')
    search_fields = ('username', 'email', 'location', 'first_name', 'last_name', 'phone_number', 'interests')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'birth_date', 'gender', 'phone_number', 'location', 'latitude', 'longitude', 'profile_picture', 'interests')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(User, CustomUserAdmin)