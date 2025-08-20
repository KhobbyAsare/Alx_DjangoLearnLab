from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Post, Comment
from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)
from .permissions import IsAuthorOrReadOnly, IsAuthorOrReadOnlyForComments
from .filters import PostFilter, CommentFilter


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on posts
    """
    queryset = Post.objects.filter(is_published=True)
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optionally restrict the returned posts to published ones,
        by filtering against query parameters in the URL.
        """
        queryset = Post.objects.all()
        
        # Show all posts to authenticated users, but filter by author for 'my_posts'
        if self.action == 'my_posts':
            return queryset.filter(author=self.request.user)
        
        # For list and retrieve, show only published posts unless it's the author
        if self.action in ['list', 'retrieve']:
            user = self.request.user
            return queryset.filter(
                Q(is_published=True) | Q(author=user)
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """
        Save the post with the current user as author
        """
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """
        Get current user's posts (including unpublished ones)
        """
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        """
        Toggle the published status of a post
        """
        post = self.get_object()
        
        # Only author can toggle publish status
        if post.author != request.user:
            return Response(
                {'error': 'You can only toggle publish status of your own posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_published = not post.is_published
        post.save()
        
        return Response({
            'message': f'Post {"published" if post.is_published else "unpublished"} successfully',
            'is_published': post.is_published
        })
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get all comments for a specific post
        """
        post = self.get_object()
        comments = post.comments.filter(is_active=True, parent=None)
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on comments
    """
    queryset = Comment.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnlyForComments]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = CommentFilter
    search_fields = ['content', 'author__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """
        Save the comment with the current user as author
        """
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        """
        Soft delete the comment by setting is_active to False
        """
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """
        Get all replies for a specific comment
        """
        comment = self.get_object()
        replies = comment.replies.filter(is_active=True)
        
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Reply to a specific comment
        """
        parent_comment = self.get_object()
        
        # Prevent replying to replies (max 1 level nesting)
        if parent_comment.parent is not None:
            return Response(
                {'error': 'Cannot reply to a reply. Please reply to the original comment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create reply with parent set to current comment
        data = request.data.copy()
        data['parent'] = parent_comment.id
        data['post'] = parent_comment.post.id
        
        serializer = CommentCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """
        Get current user's comments
        """
        comments = self.queryset.filter(author=request.user)
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
