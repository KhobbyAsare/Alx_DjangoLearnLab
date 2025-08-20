from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying author information
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    author = AuthorSerializer(read_only=True)
    reply_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'parent', 
            'created_at', 'updated_at', 'is_active', 
            'reply_count', 'is_reply'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create a new comment with the authenticated user as author
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)
    
    def validate(self, attrs):
        """
        Validate comment data
        """
        # Ensure parent comment belongs to the same post if provided
        if attrs.get('parent') and attrs.get('post'):
            if attrs['parent'].post != attrs['post']:
                raise serializers.ValidationError(
                    "Parent comment must belong to the same post"
                )
        
        # Prevent deeply nested comments (max 1 level)
        if attrs.get('parent') and attrs['parent'].parent:
            raise serializers.ValidationError(
                "Cannot reply to a reply. Please reply to the original comment."
            )
        
        return attrs


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments (simplified)
    """
    class Meta:
        model = Comment
        fields = ['content', 'post', 'parent']
    
    def create(self, validated_data):
        """
        Create a new comment with the authenticated user as author
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)
    
    def validate(self, attrs):
        """
        Validate comment creation data
        """
        # Ensure parent comment belongs to the same post if provided
        if attrs.get('parent') and attrs.get('post'):
            if attrs['parent'].post != attrs['post']:
                raise serializers.ValidationError(
                    "Parent comment must belong to the same post"
                )
        
        # Prevent deeply nested comments (max 1 level)
        if attrs.get('parent') and attrs['parent'].parent:
            raise serializers.ValidationError(
                "Cannot reply to a reply. Please reply to the original comment."
            )
        
        return attrs


class PostSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for posts with comments
    """
    author = AuthorSerializer(read_only=True)
    comment_count = serializers.ReadOnlyField()
    excerpt = serializers.ReadOnlyField()
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'image', 'author',
            'created_at', 'updated_at', 'is_published',
            'comment_count', 'excerpt', 'comments'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create a new post with the authenticated user as author
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing posts (without comments for performance)
    """
    author = AuthorSerializer(read_only=True)
    comment_count = serializers.ReadOnlyField()
    excerpt = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'excerpt', 'image', 'author',
            'created_at', 'updated_at', 'comment_count'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'comment_count', 'excerpt']


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating posts
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'is_published']
    
    def create(self, validated_data):
        """
        Create a new post with the authenticated user as author
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)
    
    def validate_title(self, value):
        """
        Validate post title
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Post title must be at least 5 characters long"
            )
        return value.strip()
    
    def validate_content(self, value):
        """
        Validate post content
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Post content must be at least 10 characters long"
            )
        return value.strip()


class NestedCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for nested comments (replies)
    """
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'created_at', 
            'updated_at', 'reply_count', 'replies'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """
        Get replies to this comment (one level only)
        """
        if obj.replies.exists():
            replies = obj.replies.filter(is_active=True)
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Detailed post serializer with nested comments
    """
    author = AuthorSerializer(read_only=True)
    comment_count = serializers.ReadOnlyField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'image', 'author',
            'created_at', 'updated_at', 'is_published',
            'comment_count', 'comments'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_comments(self, obj):
        """
        Get top-level comments with their replies
        """
        # Get only top-level comments (no parent)
        top_level_comments = obj.comments.filter(parent=None, is_active=True)
        return NestedCommentSerializer(
            top_level_comments, 
            many=True, 
            context=self.context
        ).data
