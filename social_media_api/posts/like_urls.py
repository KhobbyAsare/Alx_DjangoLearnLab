from django.urls import path
from . import like_views

app_name = 'likes'

urlpatterns = [
    # Post like actions
    path('posts/<int:pk>/like/', like_views.PostLikeView.as_view(), name='like-post'),
    path('posts/<int:pk>/unlike/', like_views.PostUnlikeView.as_view(), name='unlike-post'),
    path('posts/<int:pk>/toggle-like/', like_views.PostToggleLikeView.as_view(), name='toggle-like'),
    
    # Post like information
    path('posts/<int:pk>/like-info/', like_views.PostLikeInfoView.as_view(), name='post-like-info'),
    path('posts/<int:pk>/likes/', like_views.PostLikesListView.as_view(), name='post-likes'),
    
    # User likes
    path('my-likes/', like_views.UserLikesListView.as_view(), name='my-likes'),
    
    # Batch operations
    path('batch-like/', like_views.batch_like_action, name='batch-like'),
]
