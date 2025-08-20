from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    with additional fields for social media functionality
    """
    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        help_text="User profile picture"
    )
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        symmetrical=False,
        related_name='following',
        blank=True,
        help_text="Users who follow this user"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def follower_count(self):
        """Return the number of followers"""
        return self.followers.count()

    @property
    def following_count(self):
        """Return the number of users this user is following"""
        return self.following.count()
    
    def follow(self, user):
        """Follow another user"""
        if not self.is_following(user):
            self.following.add(user)
            return True
        return False
    
    def unfollow(self, user):
        """Unfollow another user"""
        if self.is_following(user):
            self.following.remove(user)
            return True
        return False
    
    def is_following(self, user):
        """Check if this user is following another user"""
        return self.following.filter(pk=user.pk).exists()
    
    def get_following_list(self):
        """Get list of users this user is following"""
        return self.following.all()
    
    def get_followers_list(self):
        """Get list of users who follow this user"""
        return self.followers.all()


# Alias for backwards compatibility
User = CustomUser
