from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
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
