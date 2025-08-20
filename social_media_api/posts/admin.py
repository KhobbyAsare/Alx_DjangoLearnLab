from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model
    """
    list_display = [
        'title', 'author', 'is_published', 'comment_count',
        'created_at', 'updated_at'
    ]
    list_filter = [
        'is_published', 'created_at', 'updated_at', 'author'
    ]
    search_fields = [
        'title', 'content', 'author__username', 
        'author__first_name', 'author__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'comment_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'content', 'author')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('comment_count',),
            'classes': ('collapse',)
        })
    )
    
    def comment_count(self, obj):
        """Display comment count for the post"""
        return obj.comment_count
    comment_count.short_description = 'Comments'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign the current user as author if creating a new post"""
        if not change:  # If creating a new post
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model
    """
    list_display = [
        'content_preview', 'author', 'post_title', 'is_reply',
        'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'created_at', 'post', 'author'
    ]
    search_fields = [
        'content', 'author__username', 'post__title',
        'author__first_name', 'author__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'is_reply', 'reply_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('content', 'author', 'post')
        }),
        ('Reply Settings', {
            'fields': ('parent',),
            'description': 'Select a parent comment to make this a reply'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('is_reply', 'reply_count'),
            'classes': ('collapse',)
        })
    )
    
    def content_preview(self, obj):
        """Display a preview of the comment content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def post_title(self, obj):
        """Display the title of the post this comment belongs to"""
        return obj.post.title
    post_title.short_description = 'Post'
    
    def is_reply(self, obj):
        """Display if this comment is a reply"""
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Reply?'
    
    def reply_count(self, obj):
        """Display reply count for the comment"""
        return obj.reply_count
    reply_count.short_description = 'Replies'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign the current user as author if creating a new comment"""
        if not change:  # If creating a new comment
            obj.author = request.user
        super().save_model(request, obj, form, change)
