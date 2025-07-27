from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book

# Custom admin configuration for CustomUser model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'date_of_birth', 'is_staff']

# Custom admin configuration for Book model
class BookAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('title', 'author', 'publication_year')
    
    # Add filters to the right sidebar
    list_filter = ('author', 'publication_year')
    
    # Enable search functionality
    search_fields = ('title', 'author')
    
    # Add ordering to the list view
    ordering = ('-publication_year', 'title')
    
    # Customize the form layout in the detail view
    fields = ('title', 'author', 'publication_year')
    
    # Show how many items per page
    list_per_page = 20
    
    # Add date hierarchy navigation
    date_hierarchy = 'publication_year'
    
    # Add actions to the admin
    actions = ['mark_as_featured']
    
    def mark_as_featured(self, request, queryset):
        """Custom admin action (example)"""
        # This is a placeholder for a custom action
        # In a real scenario, you might add a 'featured' field to your model
        self.message_user(request, f"{queryset.count()} books marked as featured.")
    mark_as_featured.short_description = "Mark selected books as featured"

# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Book, BookAdmin)
