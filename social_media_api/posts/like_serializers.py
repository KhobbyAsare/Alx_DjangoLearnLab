from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Like, Post

User = get_user_model()


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model
    """
    user = serializers.StringRelatedField(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'post_title', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostLikeInfoSerializer(serializers.ModelSerializer):
    """
    Serializer to show like information for a post
    """
    like_count = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    recent_likes = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'like_count', 'is_liked_by_user', 'recent_likes']
    
    def get_is_liked_by_user(self, obj):
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False
    
    def get_recent_likes(self, obj):
        """Get recent users who liked this post"""
        recent_likes = obj.likes.select_related('user').order_by('-created_at')[:5]
        return [like.user.username for like in recent_likes]


class LikeActionSerializer(serializers.Serializer):
    """
    Serializer for like/unlike actions
    """
    post = serializers.IntegerField(required=False)
    action = serializers.ChoiceField(choices=['like', 'unlike'], required=False)
    post_id = serializers.IntegerField(required=False)
    
    def validate_post_id(self, value):
        """Validate that the post exists"""
        try:
            Post.objects.get(id=value, is_published=True)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found or not published")
        return value
    
    def validate_post(self, value):
        """Validate that the post exists and is published"""
        try:
            post = Post.objects.get(id=value, is_published=True)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found or not published")
        return value
    
    def validate(self, data):
        """Validate that at least one of post or post_id is provided"""
        if not data.get('post') and not data.get('post_id'):
            raise serializers.ValidationError("Either 'post' or 'post_id' must be provided")
        return data
