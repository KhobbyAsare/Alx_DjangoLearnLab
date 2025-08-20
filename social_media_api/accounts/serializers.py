from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


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
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


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
