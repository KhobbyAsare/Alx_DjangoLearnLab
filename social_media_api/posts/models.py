from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Post(models.Model):
    """
    Model for user posts
    """
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        help_text="The user who created this post"
    )
    title = models.CharField(
        max_length=200, 
        help_text="Post title"
    )
    content = models.TextField()  # Basic TextField for post content
    image = models.ImageField(
        upload_to='posts/', 
        blank=True, 
        null=True,
        help_text="Optional image for the post"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the post was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the post was last updated"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Whether the post is visible to other users"
    )

    class Meta:
        ordering = ['-created_at']  # Newest posts first
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        db_table = 'posts_post'

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    @property
    def comment_count(self):
        """Return the number of comments on this post"""
        return self.comments.count()

    @property
    def excerpt(self):
        """Return a short excerpt of the post content"""
        return self.content[:150] + '...' if len(self.content) > 150 else self.content


class Comment(models.Model):
    """
    Model for comments on posts
    """
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="The post this comment belongs to"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="The user who created this comment"
    )
    content = models.TextField()  # Basic TextField for comment content
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='replies',
        help_text="Parent comment for nested comments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the comment was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the comment was last updated"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the comment is visible"
    )

    class Meta:
        ordering = ['created_at']  # Oldest comments first
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = 'posts_comment'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def is_reply(self):
        """Check if this is a reply to another comment"""
        return self.parent is not None

    @property
    def reply_count(self):
        """Return the number of replies to this comment"""
        return self.replies.count()
