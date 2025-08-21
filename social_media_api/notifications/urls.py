from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification list and management
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('unread/', views.UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('stats/', views.NotificationStatsView.as_view(), name='notification-stats'),
    
    # Notification actions
    path('mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('delete/<int:pk>/', views.delete_notification, name='delete-notification'),
    path('clear-read/', views.clear_read_notifications, name='clear-read-notifications'),
    path('clear-all/', views.clear_all_notifications, name='clear-all-notifications'),
]

# Available URLs:
# 
# Notifications:
# GET    /api/notifications/                     - List user notifications (with filters)
# GET    /api/notifications/<id>/               - Get specific notification (marks as read)
# GET    /api/notifications/unread/             - List unread notifications only
# GET    /api/notifications/stats/              - Get notification statistics
# POST   /api/notifications/mark-read/          - Mark specific notifications as read
# POST   /api/notifications/mark-all-read/      - Mark all notifications as read
# DELETE /api/notifications/delete/<id>/       - Delete specific notification
# DELETE /api/notifications/clear-read/        - Delete all read notifications
# DELETE /api/notifications/clear-all/         - Delete all notifications
#
# Query Parameters for notification list:
# ?read=true/false     - Filter by read status
# ?type=like/comment/follow/reply/mention - Filter by notification type
# ?recent=true         - Show only recent notifications (last 7 days)
