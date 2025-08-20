from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import User

# Use get_user_model() for better flexibility
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Verify that password and password_confirm match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TokenRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with automatic token creation
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'password', 'password_confirm', 'token'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Verify that password and password_confirm match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance with token
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create token for the new user
        token = Token.objects.create(user=user)
        
        return user, token


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate and authenticate the user
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    attrs['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled')
            else:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Must provide username and password')

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management
    """
    follower_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    followers = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'follower_count', 'following_count',
            'followers', 'date_joined', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'profile_picture')

    def update(self, instance, validated_data):
        """
        Update and return the user instance
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (minimal info)
    """
    follower_count = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'bio', 'profile_picture', 'follower_count'
        )
        read_only_fields = ('id', 'username', 'follower_count')


class FollowSerializer(serializers.Serializer):
    """
    Serializer for follow/unfollow operations
    """
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """
        Validate that the user exists and is not the current user
        """
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        request = self.context.get('request')
        if request and request.user.id == value:
            raise serializers.ValidationError("You cannot follow yourself")
        
        return value


class FollowerSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying follower information
    """
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'bio', 'profile_picture', 'is_following'
        )
        read_only_fields = ('id', 'username', 'first_name', 'last_name')
    
    def get_is_following(self, obj):
        """
        Check if current user is following this user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_following(obj)
        return False


class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying following information
    """
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'bio', 'profile_picture', 'is_following'
        )
        read_only_fields = ('id', 'username', 'first_name', 'last_name')
    
    def get_is_following(self, obj):
        """
        This will always be True since these are users the current user is following
        """
        return True


class UserSocialSerializer(serializers.ModelSerializer):
    """
    Enhanced user serializer with social information
    """
    follower_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'bio',
            'profile_picture', 'follower_count', 'following_count',
            'is_following', 'is_followed_by', 'date_joined'
        )
        read_only_fields = ('id', 'username', 'date_joined')
    
    def get_is_following(self, obj):
        """
        Check if current user is following this user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_following(obj)
        return False
    
    def get_is_followed_by(self, obj):
        """
        Check if this user is following the current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_following(request.user)
        return False
