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
    
    # Follow/Unfollow endpoint
    path('follow/<str:username>/', views.follow_user, name='follow-user'),
]
