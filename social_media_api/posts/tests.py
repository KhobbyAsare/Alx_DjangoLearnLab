from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Post

User = get_user_model()


class FeedViewTestCase(APITestCase):
    """
    Test cases for the Feed view
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com', 
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # Create tokens
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        # User1 follows User2
        self.user1.following.add(self.user2)
        
        # Create posts
        self.post1 = Post.objects.create(
            title='Post by User2',
            content='This is a post by user2',
            author=self.user2,
            is_published=True
        )
        self.post2 = Post.objects.create(
            title='Another post by User2', 
            content='Another post by user2',
            author=self.user2,
            is_published=True
        )
        self.post3 = Post.objects.create(
            title='Post by User3',
            content='This is a post by user3',
            author=self.user3,
            is_published=True
        )
        
        self.client = APIClient()
    
    def test_feed_shows_followed_users_posts(self):
        """
        Test that feed shows posts from followed users only
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        response = self.client.get('/api/posts/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Should show 2 posts from user2
        
        # Check that posts are from followed user (user2)
        for post in response.data['results']:
            self.assertEqual(post['author']['username'], 'user2')
    
    def test_feed_ordered_by_creation_date(self):
        """
        Test that feed posts are ordered by creation date (newest first)
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        response = self.client.get('/api/posts/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        posts = response.data['results']
        
        # Check that posts are ordered by newest first
        if len(posts) > 1:
            for i in range(len(posts) - 1):
                self.assertGreaterEqual(posts[i]['created_at'], posts[i+1]['created_at'])
    
    def test_feed_requires_authentication(self):
        """
        Test that feed requires authentication
        """
        response = self.client.get('/api/posts/feed/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_feed_empty_when_not_following_anyone(self):
        """
        Test that feed shows helpful message when not following anyone
        """
        # Authenticate as user2 who doesn't follow anyone
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
        response = self.client.get('/api/posts/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following_count'], 0)
        self.assertIn('You are not following anyone yet', response.data['message'])
