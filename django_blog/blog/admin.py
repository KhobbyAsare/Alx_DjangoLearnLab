from django.contrib import admin
from .models import Post, Comment, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model"""
    list_display = ('name', 'slug', 'post_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    def post_count(self, obj):
        """Display number of posts with this tag"""
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model"""
    list_display = ('title', 'author', 'published_date', 'tag_list')
    list_filter = ('published_date', 'author', 'tags')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_date'
    filter_horizontal = ('tags',)
    
    def tag_list(self, obj):
        """Display comma-separated list of tags"""
        return ', '.join([tag.name for tag in obj.tags.all()])
    tag_list.short_description = 'Tags'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model"""
    list_display = ('post', 'author', 'created_at', 'content_preview')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'author__username')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        """Display truncated content preview"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
