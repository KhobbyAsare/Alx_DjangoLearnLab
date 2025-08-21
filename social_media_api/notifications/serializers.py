from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Notification

User = get_user_model()


class NotificationActorSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for the actor in notifications
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    actor = NotificationActorSerializer(read_only=True)
    message = serializers.SerializerMethodField()
    target_object = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'verb', 'message', 'target_object', 
            'is_read', 'is_recent', 'created_at', 'read_at', 'time_since'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_message(self, obj):
        """Get the user-friendly message for the notification"""
        return obj.get_message()
    
    def get_target_object(self, obj):
        """Get basic information about the target object"""
        if obj.target:
            target_data = {
                'type': obj.target_content_type.model,
                'id': obj.target_object_id,
            }
            
            # Add specific fields based on target type
            if hasattr(obj.target, 'title'):
                target_data['title'] = obj.target.title
            elif hasattr(obj.target, 'content'):
                content = obj.target.content
                target_data['content'] = content[:50] + '...' if len(content) > 50 else content
            
            return target_data
        return None
    
    def get_time_since(self, obj):
        """Get a human-readable time since notification was created"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at) + " ago"


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for notification lists
    """
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    message = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'actor_username', 'verb', 'message', 
            'is_read', 'is_recent', 'created_at'
        ]
    
    def get_message(self, obj):
        """Get the user-friendly message for the notification"""
        return obj.get_message()


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    class Meta:
        model = Notification
        fields = ['recipient', 'actor', 'verb', 'target_content_type', 'target_object_id', 'message']
    
    def validate(self, data):
        """Validate the notification data"""
        # Don't create notifications for self-actions
        if data['recipient'] == data['actor']:
            raise serializers.ValidationError("Cannot create notification for self-actions")
        
        return data


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer for notification statistics
    """
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    recent_count = serializers.IntegerField()
    by_type = serializers.DictField()
