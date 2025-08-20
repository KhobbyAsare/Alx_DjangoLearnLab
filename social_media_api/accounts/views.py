from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.shortcuts import get_object_or_404

from .models import User, CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    FollowSerializer,
    FollowerSerializer,
    FollowingSerializer,
    UserSocialSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration
    """
    queryset = CustomUser.objects.all()
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
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'


class UserListView(generics.ListAPIView):
    """
    View for listing all users
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]


class FollowersListView(generics.GenericAPIView):
    """
    View for listing a user's followers
    """
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id=None, *args, **kwargs):
        """
        Get list of followers for a specific user (or current user if no user_id provided)
        """
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        followers = user.followers.all()
        serializer = self.get_serializer(followers, many=True, context={'request': request})
        
        return Response({
            'user': user.username,
            'follower_count': followers.count(),
            'followers': serializer.data
        }, status=status.HTTP_200_OK)


class FollowingListView(generics.GenericAPIView):
    """
    View for listing users that a user is following
    """
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id=None, *args, **kwargs):
        """
        Get list of users that a specific user is following (or current user if no user_id provided)
        """
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        following = user.following.all()
        serializer = self.get_serializer(following, many=True, context={'request': request})
        
        return Response({
            'user': user.username,
            'following_count': following.count(),
            'following': serializer.data
        }, status=status.HTTP_200_OK)


class UserSocialDetailView(generics.GenericAPIView):
    """
    View for retrieving detailed social information about a user
    """
    serializer_class = UserSocialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id, *args, **kwargs):
        """
        Get detailed social information for a specific user
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowUserView(generics.GenericAPIView):
    """
    View for following a user
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    
    def post(self, request, user_id=None, *args, **kwargs):
        """
        Follow a user by user_id (from URL parameter or request data)
        """
        # Get user_id from URL parameter if provided, otherwise from request data
        if user_id is not None:
            # URL parameter provided
            target_user_id = user_id
        else:
            # Get from request data using serializer
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            target_user_id = serializer.validated_data['user_id']
        
        try:
            user_to_follow = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_user = request.user
        
        # Check if already following
        if current_user.following.filter(id=target_user_id).exists():
            return Response({
                'error': f'You are already following {user_to_follow.username}',
                'is_following': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Follow the user
        current_user.following.add(user_to_follow)
        
        return Response({
            'message': f'You are now following {user_to_follow.username}',
            'is_following': True,
            'user': UserSocialSerializer(user_to_follow, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class UnfollowUserView(generics.GenericAPIView):
    """
    View for unfollowing a user
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    
    def post(self, request, user_id=None, *args, **kwargs):
        """
        Unfollow a user by user_id (from URL parameter or request data)
        """
        # Get user_id from URL parameter if provided, otherwise from request data
        if user_id is not None:
            # URL parameter provided
            target_user_id = user_id
        else:
            # Get from request data using serializer
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            target_user_id = serializer.validated_data['user_id']
        
        try:
            user_to_unfollow = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_user = request.user
        
        # Check if not following
        if not current_user.following.filter(id=target_user_id).exists():
            return Response({
                'error': f'You are not following {user_to_unfollow.username}',
                'is_following': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Unfollow the user
        current_user.following.remove(user_to_unfollow)
        
        return Response({
            'message': f'You unfollowed {user_to_unfollow.username}',
            'is_following': False,
            'user': UserSocialSerializer(user_to_unfollow, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class ToggleFollowUserView(generics.GenericAPIView):
    """
    View for toggling follow/unfollow status (combined follow/unfollow)
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    
    def post(self, request, *args, **kwargs):
        """
        Toggle follow/unfollow status for a user by user_id
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        target_user = User.objects.get(id=user_id)
        current_user = request.user
        
        # Toggle follow status
        if current_user.following.filter(id=user_id).exists():
            # Unfollow
            current_user.following.remove(target_user)
            message = f'You unfollowed {target_user.username}'
            is_following = False
        else:
            # Follow
            current_user.following.add(target_user)
            message = f'You are now following {target_user.username}'
            is_following = True
        
        return Response({
            'message': message,
            'is_following': is_following,
            'user': UserSocialSerializer(target_user, context={'request': request}).data
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    """
    Legacy view for following/unfollowing a user by username (kept for backwards compatibility)
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
