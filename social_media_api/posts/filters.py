import django_filters
from django.db.models import Q
from .models import Post, Comment


class PostFilter(django_filters.FilterSet):
    """
    Filter class for Post model with various filtering options
    """
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter posts by title (case-insensitive partial match)'
    )
    
    content = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        help_text='Filter posts by content (case-insensitive partial match)'
    )
    
    author_username = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='iexact',
        help_text='Filter posts by author username (exact match)'
    )
    
    author_name = django_filters.CharFilter(
        method='filter_by_author_name',
        help_text='Filter posts by author first name or last name'
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter posts created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter posts created before this date/time'
    )
    
    is_published = django_filters.BooleanFilter(
        field_name='is_published',
        help_text='Filter posts by published status'
    )
    
    has_image = django_filters.BooleanFilter(
        method='filter_has_image',
        help_text='Filter posts that have an image attached'
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Search in title, content, and author username'
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'author_username', 'author_name',
            'created_after', 'created_before', 'is_published', 
            'has_image', 'search'
        ]
    
    def filter_by_author_name(self, queryset, name, value):
        """
        Filter posts by author's first name or last name
        """
        return queryset.filter(
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value)
        )
    
    def filter_has_image(self, queryset, name, value):
        """
        Filter posts that have an image attached
        """
        if value:
            return queryset.exclude(image='')
        else:
            return queryset.filter(image='')
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields
        """
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value) |
            Q(author__username__icontains=value) |
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value)
        ).distinct()


class CommentFilter(django_filters.FilterSet):
    """
    Filter class for Comment model with various filtering options
    """
    content = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        help_text='Filter comments by content (case-insensitive partial match)'
    )
    
    author_username = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='iexact',
        help_text='Filter comments by author username (exact match)'
    )
    
    post_id = django_filters.NumberFilter(
        field_name='post__id',
        help_text='Filter comments by post ID'
    )
    
    post_title = django_filters.CharFilter(
        field_name='post__title',
        lookup_expr='icontains',
        help_text='Filter comments by post title'
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter comments created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter comments created before this date/time'
    )
    
    is_reply = django_filters.BooleanFilter(
        method='filter_is_reply',
        help_text='Filter comments that are replies to other comments'
    )
    
    parent_comment = django_filters.NumberFilter(
        field_name='parent__id',
        help_text='Filter comments by parent comment ID'
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Search in content, author username, and post title'
    )
    
    class Meta:
        model = Comment
        fields = [
            'content', 'author_username', 'post_id', 'post_title',
            'created_after', 'created_before', 'is_reply',
            'parent_comment', 'search'
        ]
    
    def filter_is_reply(self, queryset, name, value):
        """
        Filter comments that are replies (have a parent) or not
        """
        if value:
            return queryset.exclude(parent__isnull=True)
        else:
            return queryset.filter(parent__isnull=True)
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields
        """
        return queryset.filter(
            Q(content__icontains=value) |
            Q(author__username__icontains=value) |
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value) |
            Q(post__title__icontains=value)
        ).distinct()
