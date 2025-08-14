from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager


class Tag(models.Model):
    """Tag model for categorizing posts"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return URL for viewing posts with this tag"""
        return reverse('posts_by_tag', kwargs={'slug': self.slug})
    
    @property
    def post_count(self):
        """Return number of posts with this tag"""
        return self.posts.count()


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # Custom tagging system
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    # Django-taggit integration (alternative tagging system)
    taggit_tags = TaggableManager(blank=True, help_text='A comma-separated list of tags.')
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return URL for viewing this post"""
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    @property
    def tag_list(self):
        """Return comma-separated list of tag names"""
        return ', '.join([tag.name for tag in self.tags.all()])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest comments first
        
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
