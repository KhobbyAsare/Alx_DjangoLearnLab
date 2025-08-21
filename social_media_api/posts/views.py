from rest_framework import viewsets, status, filters, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from .models import Post, Comment, Like
from notifications.models import Notification
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
    queryset = Comment.objects.all()  # Base queryset for all comments
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
    
    def get_queryset(self):
        """
        Return queryset for comments with optional filtering
        """
        queryset = Comment.objects.all()
        
        # Filter out inactive comments for most views
        if self.action not in ['destroy', 'update', 'partial_update']:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
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


class FeedView(generics.ListAPIView):
    """
    View that generates a feed based on the posts from users that the current user follows.
    Posts are ordered by creation date, showing the most recent posts at the top.
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
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
        Return posts from users that the current user follows,
        ordered by creation date with most recent first.
        """
        user = self.request.user
        
        # Get users that the current user is following
        following_users = user.following.all()
        
        # Filter posts by authors that the current user follows
        # Only show published posts  
        queryset = Post.objects.filter(author__in=following_users).order_by('-created_at')
        queryset = queryset.filter(is_published=True)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to provide additional context in response
        """
        queryset = self.filter_queryset(self.get_queryset())
        following_count = request.user.following.all().count()
        
        # If user is not following anyone, return helpful message
        if following_count == 0:
            return Response({
                'message': 'You are not following anyone yet. Follow some users to see their posts in your feed!',
                'results': [],
                'count': 0,
                'following_count': following_count
            })
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['following_count'] = following_count
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'following_count': following_count
        })


class LikePostView(generics.GenericAPIView):
    """
    View to like a post and create appropriate notifications
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """
        Like a post by its primary key
        """
        post = generics.get_object_or_404(Post, pk=pk)
        
        # Prevent users from liking their own posts
        if post.author == request.user:
            return Response(
                {'error': 'You cannot like your own post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to create a like, get existing if already liked
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            # Create notification for post author
            if post.author != request.user:  # Don't notify self
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    verb='like',
                    target=post,
                    message=f"{request.user.username} liked your post: {post.title}"
                )
            
            return Response({
                'message': 'Post liked successfully',
                'liked': True,
                'like_count': post.like_count
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'You have already liked this post',
                'liked': True,
                'like_count': post.like_count
            }, status=status.HTTP_200_OK)


class UnlikePostView(generics.GenericAPIView):
    """
    View to unlike a post and remove appropriate notifications
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        """
        Unlike a post by its primary key
        """
        post = generics.get_object_or_404(Post, pk=pk)
        
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            
            # Remove notification if exists
            try:
                notification = Notification.objects.get(
                    recipient=post.author,
                    actor=request.user,
                    verb='like',
                    target_content_type=ContentType.objects.get_for_model(Post),
                    target_object_id=post.id
                )
                notification.delete()
            except Notification.DoesNotExist:
                pass  # Notification might not exist
            
            return Response({
                'message': 'Post unliked successfully',
                'liked': False,
                'like_count': post.like_count
            }, status=status.HTTP_200_OK)
            
        except Like.DoesNotExist:
            return Response({
                'error': 'You have not liked this post yet',
                'liked': False,
                'like_count': post.like_count
            }, status=status.HTTP_400_BAD_REQUEST)
