from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.shortcuts import get_object_or_404

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserListSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new user and return user data with token
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create or get token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    View for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create or get token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Login the user
        login(request, user)
        
        # Return user data with token
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Return the current authenticated user
        """
        return self.request.user

    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method
        """
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer


class UserDetailView(generics.RetrieveAPIView):
    """
    View for retrieving other users' profiles
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'


class UserListView(generics.ListAPIView):
    """
    View for listing all users
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    """
    View for following/unfollowing a user
    """
    try:
        user_to_follow = get_object_or_404(User, username=username)
        current_user = request.user
        
        if user_to_follow == current_user:
            return Response({
                'error': 'You cannot follow yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already following
        if current_user.following.filter(username=username).exists():
            # Unfollow
            current_user.following.remove(user_to_follow)
            message = f'You unfollowed {username}'
            is_following = False
        else:
            # Follow
            current_user.following.add(user_to_follow)
            message = f'You are now following {username}'
            is_following = True
        
        return Response({
            'message': message,
            'is_following': is_following
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_view(request):
    """
    View for user logout (delete token)
    """
    if request.user.is_authenticated:
        # Delete the user's token to log them out
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({
                'message': 'User was not logged in'
            }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'User not authenticated'
    }, status=status.HTTP_401_UNAUTHORIZED)
