from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Follow/Unfollow endpoints
    path('follow/<str:username>/', views.follow_user, name='follow-user'),  # Legacy
    path('follow/<int:user_id>/', views.FollowUserView.as_view(), name='follow-user-id'),
    path('unfollow/<int:user_id>/', views.UnfollowUserView.as_view(), name='unfollow-user-id'),
    path('toggle-follow/', views.ToggleFollowUserView.as_view(), name='toggle-follow'),
    
    # Social relationship endpoints
    path('followers/', views.FollowersListView.as_view(), name='my-followers'),
    path('followers/<int:user_id>/', views.FollowersListView.as_view(), name='user-followers'),
    path('following/', views.FollowingListView.as_view(), name='my-following'),
    path('following/<int:user_id>/', views.FollowingListView.as_view(), name='user-following'),
    path('social/<int:user_id>/', views.UserSocialDetailView.as_view(), name='user-social-detail'),
]
