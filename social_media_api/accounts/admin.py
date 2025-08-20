from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin with additional fields
    """
    # Fields to display in the user list
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'date_joined', 'follower_count'
    )
    
    # Add search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Add filters
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    # Customize the fieldsets for the user edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Social Media Fields', {
            'fields': ('bio', 'profile_picture', 'followers')
        }),
    )
    
    # Add custom method to display follower count
    def follower_count(self, obj):
        return obj.follower_count
    follower_count.short_description = 'Followers'
