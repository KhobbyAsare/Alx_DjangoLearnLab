from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import like_views

app_name = 'posts'

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    # Custom feed view for posts from followed users
    path('feed/', views.FeedView.as_view(), name='feed'),
    
    # Like/Unlike endpoints
    path('posts/<int:pk>/like/', like_views.PostLikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', like_views.PostUnlikeView.as_view(), name='post-unlike'),
    path('posts/<int:pk>/toggle-like/', like_views.PostToggleLikeView.as_view(), name='post-toggle-like'),
    path('posts/<int:pk>/like-info/', like_views.PostLikeInfoView.as_view(), name='post-like-info'),
    path('posts/<int:pk>/likes/', like_views.PostLikesListView.as_view(), name='post-likes-list'),
    
    # User likes
    path('my-likes/', like_views.UserLikesListView.as_view(), name='user-likes'),
    path('batch-like/', like_views.batch_like_action, name='batch-like'),
]

# Available URLs:
# 
# Posts:
# GET    /api/posts/                 - List all posts
# POST   /api/posts/                 - Create a new post
# GET    /api/posts/{id}/            - Retrieve a specific post
# PUT    /api/posts/{id}/            - Update a specific post (full)
# PATCH  /api/posts/{id}/            - Update a specific post (partial)
# DELETE /api/posts/{id}/            - Delete a specific post
# GET    /api/posts/my_posts/        - Get current user's posts
# POST   /api/posts/{id}/toggle_publish/ - Toggle post publish status
# GET    /api/posts/{id}/comments/   - Get comments for a specific post
# GET    /api/posts/feed/            - Get personalized feed from followed users
#
# Comments:
# GET    /api/comments/              - List all comments
# POST   /api/comments/              - Create a new comment
# GET    /api/comments/{id}/         - Retrieve a specific comment
# PUT    /api/comments/{id}/         - Update a specific comment (full)
# PATCH  /api/comments/{id}/         - Update a specific comment (partial)  
# DELETE /api/comments/{id}/         - Delete a specific comment
# GET    /api/comments/my_comments/  - Get current user's comments
# GET    /api/comments/{id}/replies/ - Get replies for a specific comment
# POST   /api/comments/{id}/reply/   - Reply to a specific comment
