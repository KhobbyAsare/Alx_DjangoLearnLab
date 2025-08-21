from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def create_notification(recipient, actor, verb, target=None, message=None):
    """
    Create a notification with the given parameters
    
    Args:
        recipient: User who will receive the notification
        actor: User who performed the action
        verb: Type of action (like, comment, follow, etc.)
        target: The object being acted upon (optional)
        message: Custom message (optional)
    
    Returns:
        Notification instance or None if not created
    """
    # Don't create notifications for self-actions
    if recipient == actor:
        return None
    
    # Prepare notification data
    notification_data = {
        'recipient': recipient,
        'actor': actor,
        'verb': verb,
        'message': message or '',
    }
    
    # Add target if provided
    if target:
        notification_data.update({
            'target_content_type': ContentType.objects.get_for_model(target),
            'target_object_id': target.id,
        })
    
    # Create or get existing notification to avoid duplicates
    notification, created = Notification.objects.get_or_create(
        **notification_data,
        defaults={'message': message or ''}
    )
    
    return notification if created else None


def create_like_notification(post, liker):
    """
    Create a notification when someone likes a post
    """
    return create_notification(
        recipient=post.author,
        actor=liker,
        verb='like',
        target=post
    )


def create_comment_notification(comment):
    """
    Create a notification when someone comments on a post
    """
    # Notification for post author (if not the commenter)
    post_notification = create_notification(
        recipient=comment.post.author,
        actor=comment.author,
        verb='comment',
        target=comment.post
    )
    
    # If it's a reply, also notify the parent comment author
    reply_notification = None
    if comment.parent and comment.parent.author != comment.author:
        reply_notification = create_notification(
            recipient=comment.parent.author,
            actor=comment.author,
            verb='reply',
            target=comment.parent
        )
    
    return post_notification, reply_notification


def create_follow_notification(follower, followed_user):
    """
    Create a notification when someone follows a user
    """
    return create_notification(
        recipient=followed_user,
        actor=follower,
        verb='follow'
    )


def delete_like_notification(post, unliker):
    """
    Delete notification when someone unlikes a post
    """
    try:
        notification = Notification.objects.get(
            recipient=post.author,
            actor=unliker,
            verb='like',
            target_content_type=ContentType.objects.get_for_model(post),
            target_object_id=post.id
        )
        notification.delete()
        return True
    except Notification.DoesNotExist:
        return False


def delete_follow_notification(unfollower, unfollowed_user):
    """
    Delete notification when someone unfollows a user
    """
    try:
        notification = Notification.objects.get(
            recipient=unfollowed_user,
            actor=unfollower,
            verb='follow'
        )
        notification.delete()
        return True
    except Notification.DoesNotExist:
        return False


def mark_notifications_as_read(user, notification_ids=None):
    """
    Mark notifications as read for a user
    
    Args:
        user: The user whose notifications to mark as read
        notification_ids: List of specific notification IDs (optional)
    
    Returns:
        Number of notifications marked as read
    """
    queryset = user.notifications.filter(is_read=False)
    
    if notification_ids:
        queryset = queryset.filter(id__in=notification_ids)
    
    count = 0
    for notification in queryset:
        notification.mark_as_read()
        count += 1
    
    return count


def get_notification_stats(user):
    """
    Get notification statistics for a user
    
    Returns:
        Dictionary with notification counts and stats
    """
    notifications = user.notifications.all()
    
    stats = {
        'total_count': notifications.count(),
        'unread_count': notifications.filter(is_read=False).count(),
        'recent_count': notifications.filter(is_read=False).count(),  # This could be last 24h
        'by_type': {}
    }
    
    # Count by notification type
    from django.db.models import Count
    type_counts = notifications.values('verb').annotate(count=Count('verb'))
    
    for item in type_counts:
        stats['by_type'][item['verb']] = item['count']
    
    return stats
