from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Notification
from .serializers import (
    NotificationSerializer, 
    NotificationListSerializer, 
    NotificationStatsSerializer
)
from .utils import mark_notifications_as_read, get_notification_stats


class NotificationListView(generics.ListAPIView):
    """
    View for listing user notifications
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get notifications for the current user
        """
        user = self.request.user
        queryset = user.notifications.select_related('actor').order_by('-created_at')
        
        # Filter by read status if requested
        read_filter = self.request.query_params.get('read')
        if read_filter is not None:
            if read_filter.lower() == 'true':
                queryset = queryset.filter(is_read=True)
            elif read_filter.lower() == 'false':
                queryset = queryset.filter(is_read=False)
        
        # Filter by notification type if requested
        verb_filter = self.request.query_params.get('type')
        if verb_filter:
            queryset = queryset.filter(verb=verb_filter)
        
        # Filter by recent notifications (last 7 days)
        recent_filter = self.request.query_params.get('recent')
        if recent_filter and recent_filter.lower() == 'true':
            week_ago = timezone.now() - timezone.timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to include additional metadata
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add notification stats
            stats = get_notification_stats(request.user)
            response.data['stats'] = stats
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        stats = get_notification_stats(request.user)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'stats': stats
        })


class NotificationDetailView(generics.RetrieveAPIView):
    """
    View for retrieving a specific notification
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Only allow users to see their own notifications
        """
        return self.request.user.notifications.select_related('actor')
    
    def retrieve(self, request, *args, **kwargs):
        """
        Mark notification as read when viewed
        """
        instance = self.get_object()
        
        # Mark as read if not already read
        if not instance.is_read:
            instance.mark_as_read()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UnreadNotificationsView(generics.ListAPIView):
    """
    View for listing only unread notifications
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get only unread notifications for the current user
        """
        return self.request.user.notifications.filter(
            is_read=False
        ).select_related('actor').order_by('-created_at')


class NotificationStatsView(generics.GenericAPIView):
    """
    View for getting notification statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get notification statistics for the current user
        """
        stats = get_notification_stats(request.user)
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """
    Mark notifications as read
    """
    # Get notification IDs from request (optional)
    notification_ids = request.data.get('notification_ids', None)
    
    if notification_ids:
        # Validate that all notifications belong to the user
        user_notifications = request.user.notifications.filter(
            id__in=notification_ids,
            is_read=False
        )
        
        if len(user_notifications) != len(notification_ids):
            return Response({
                'error': 'Some notifications not found or already read'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark notifications as read
    count = mark_notifications_as_read(request.user, notification_ids)
    
    return Response({
        'message': f'{count} notifications marked as read',
        'count': count
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current user
    """
    count = mark_notifications_as_read(request.user)
    
    return Response({
        'message': f'All {count} notifications marked as read',
        'count': count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """
    Delete a specific notification
    """
    try:
        notification = request.user.notifications.get(pk=pk)
        notification.delete()
        
        return Response({
            'message': 'Notification deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
        
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_read_notifications(request):
    """
    Delete all read notifications for the current user
    """
    count, _ = request.user.notifications.filter(is_read=True).delete()
    
    return Response({
        'message': f'{count} read notifications deleted',
        'count': count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_all_notifications(request):
    """
    Delete all notifications for the current user (use with caution)
    """
    count, _ = request.user.notifications.all().delete()
    
    return Response({
        'message': f'All {count} notifications deleted',
        'count': count
    })
