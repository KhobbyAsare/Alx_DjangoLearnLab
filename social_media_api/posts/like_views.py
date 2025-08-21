from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from .models import Post, Like
from .like_serializers import LikeSerializer, PostLikeInfoSerializer, LikeActionSerializer
from notifications.utils import create_like_notification, delete_like_notification

User = get_user_model()


class PostLikeView(generics.GenericAPIView):
    """
    View for liking a post
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """
        Like a post
        """
        post = get_object_or_404(Post, pk=pk, is_published=True)
        user = request.user
        
        # Check if user already liked this post
        if post.is_liked_by(user):
            return Response({
                'error': 'You have already liked this post',
                'liked': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the like
            like = Like.objects.create(post=post, user=user)
            
            # Create notification for post author
            create_like_notification(post, user)
            
            # Return post like information
            post_serializer = PostLikeInfoSerializer(post, context={'request': request})
            
            return Response({
                'message': f'You liked "{post.title}"',
                'liked': True,
                'post_info': post_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            # Handle race condition where like was created between check and creation
            return Response({
                'error': 'You have already liked this post',
                'liked': True
            }, status=status.HTTP_400_BAD_REQUEST)


class PostUnlikeView(generics.GenericAPIView):
    """
    View for unliking a post
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """
        Unlike a post
        """
        post = get_object_or_404(Post, pk=pk, is_published=True)
        user = request.user
        
        # Check if user has liked this post
        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            
            # Delete the corresponding notification
            delete_like_notification(post, user)
            
            # Return post like information
            post_serializer = PostLikeInfoSerializer(post, context={'request': request})
            
            return Response({
                'message': f'You unliked "{post.title}"',
                'liked': False,
                'post_info': post_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Like.DoesNotExist:
            return Response({
                'error': 'You have not liked this post',
                'liked': False
            }, status=status.HTTP_400_BAD_REQUEST)


class PostToggleLikeView(generics.GenericAPIView):
    """
    View for toggling like status of a post
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """
        Toggle like status for a post
        """
        post = get_object_or_404(Post, pk=pk, is_published=True)
        user = request.user
        
        try:
            # Try to get existing like
            like = Like.objects.get(post=post, user=user)
            # If it exists, unlike the post
            like.delete()
            delete_like_notification(post, user)
            
            action = 'unliked'
            liked = False
            http_status = status.HTTP_200_OK
            
        except Like.DoesNotExist:
            # If it doesn't exist, like the post
            try:
                Like.objects.create(post=post, user=user)
                create_like_notification(post, user)
                
                action = 'liked'
                liked = True
                http_status = status.HTTP_201_CREATED
                
            except IntegrityError:
                # Handle race condition
                action = 'already liked'
                liked = True
                http_status = status.HTTP_200_OK
        
        # Return post like information
        post_serializer = PostLikeInfoSerializer(post, context={'request': request})
        
        return Response({
            'message': f'You {action} "{post.title}"',
            'liked': liked,
            'post_info': post_serializer.data
        }, status=http_status)


class PostLikeInfoView(generics.RetrieveAPIView):
    """
    View for getting like information about a post
    """
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostLikeInfoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostLikesListView(generics.ListAPIView):
    """
    View for listing users who liked a post
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get likes for a specific post
        """
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id, is_published=True)
        return Like.objects.filter(post=post).select_related('user', 'post')


class UserLikesListView(generics.ListAPIView):
    """
    View for listing posts liked by the current user
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get posts liked by the current user
        """
        return Like.objects.filter(
            user=self.request.user,
            post__is_published=True
        ).select_related('user', 'post').order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_like_action(request):
    """
    Perform batch like/unlike actions on multiple posts
    """
    serializer = LikeActionSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    
    results = []
    user = request.user
    
    for item in serializer.validated_data:
        post_id = item['post_id']
        action = item['action']
        
        try:
            post = Post.objects.get(id=post_id, is_published=True)
            
            if action == 'like':
                if not post.is_liked_by(user):
                    Like.objects.create(post=post, user=user)
                    create_like_notification(post, user)
                    results.append({
                        'post_id': post_id,
                        'action': 'liked',
                        'success': True
                    })
                else:
                    results.append({
                        'post_id': post_id,
                        'action': 'already_liked',
                        'success': False,
                        'error': 'Already liked'
                    })
            
            elif action == 'unlike':
                try:
                    like = Like.objects.get(post=post, user=user)
                    like.delete()
                    delete_like_notification(post, user)
                    results.append({
                        'post_id': post_id,
                        'action': 'unliked',
                        'success': True
                    })
                except Like.DoesNotExist:
                    results.append({
                        'post_id': post_id,
                        'action': 'not_liked',
                        'success': False,
                        'error': 'Not previously liked'
                    })
        
        except Post.DoesNotExist:
            results.append({
                'post_id': post_id,
                'action': 'error',
                'success': False,
                'error': 'Post not found'
            })
        except IntegrityError:
            results.append({
                'post_id': post_id,
                'action': 'error',
                'success': False,
                'error': 'Database integrity error'
            })
    
    return Response({
        'results': results,
        'success_count': sum(1 for r in results if r['success']),
        'error_count': sum(1 for r in results if not r['success'])
    }, status=status.HTTP_200_OK)
