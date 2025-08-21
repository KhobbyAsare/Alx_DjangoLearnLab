from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """
    Model for user notifications - tracks various interactions and activities
    """
    
    # Notification types
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('reply', 'Reply'),
        ('mention', 'Mention'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who receives this notification"
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actor_notifications',
        help_text="The user who performed the action"
    )
    verb = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        help_text="The type of action that triggered this notification"
    )
    
    # GenericForeignKey for the target object (post, comment, etc.)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Additional fields
    message = models.TextField(
        blank=True,
        help_text="Custom message for the notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the recipient has read this notification"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was created"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was marked as read"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        db_table = 'notifications_notification'
        
        # Prevent duplicate notifications for the same action
        unique_together = [
            ['recipient', 'actor', 'verb', 'target_content_type', 'target_object_id']
        ]
    
    def __str__(self):
        target_str = f" on {self.target}" if self.target else ""
        return f"{self.actor.username} {self.get_verb_display().lower()}d{target_str}"
    
    def mark_as_read(self):
        """Mark the notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_recent(self):
        """Check if notification was created in the last 24 hours"""
        return (timezone.now() - self.created_at).days < 1
    
    def get_message(self):
        """Generate a user-friendly message for the notification"""
        if self.message:
            return self.message
            
        # Generate default messages based on verb
        verb_messages = {
            'like': f"{self.actor.username} liked your post",
            'comment': f"{self.actor.username} commented on your post",
            'follow': f"{self.actor.username} started following you",
            'reply': f"{self.actor.username} replied to your comment",
            'mention': f"{self.actor.username} mentioned you",
        }
        
        return verb_messages.get(self.verb, f"{self.actor.username} interacted with your content")
