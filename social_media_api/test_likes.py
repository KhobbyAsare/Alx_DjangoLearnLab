#!/usr/bin/env python
"""
Test script for like functionality
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from posts.models import Post, Like
from notifications.models import Notification
from django.db import transaction

User = get_user_model()

def setup_test_data():
    """Create test users and posts"""
    # Create test users
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={'email': 'user1@test.com'}
    )
    user2, created = User.objects.get_or_create(
        username='testuser2', 
        defaults={'email': 'user2@test.com'}
    )
    
    # Create test posts
    post1, created = Post.objects.get_or_create(
        title='Test Post 1',
        defaults={
            'content': 'This is a test post for like functionality',
            'author': user1,
            'is_published': True
        }
    )
    
    post2, created = Post.objects.get_or_create(
        title='Test Post 2',
        defaults={
            'content': 'Another test post for like functionality',
            'author': user2,
            'is_published': True
        }
    )
    
    return user1, user2, post1, post2

def test_like_functionality():
    """Test the core like functionality"""
    print("Setting up test data...")
    user1, user2, post1, post2 = setup_test_data()
    
    # Clear any existing likes for clean test
    Like.objects.filter(post__in=[post1, post2]).delete()
    
    print(f"Created users: {user1.username}, {user2.username}")
    print(f"Created posts: {post1.title}, {post2.title}")
    
    # Test 1: User2 likes User1's post
    print("\n--- Test 1: Creating a like ---")
    like1 = Like.objects.create(user=user2, post=post1)
    print(f"✓ {user2.username} liked '{post1.title}'")
    print(f"Post like count: {post1.like_count}")
    print(f"Is liked by {user2.username}: {post1.is_liked_by(user2)}")
    print(f"Is liked by {user1.username}: {post1.is_liked_by(user1)}")
    
    # Test 2: Check notifications
    print("\n--- Test 2: Checking notifications ---")
    notification = Notification.objects.filter(
        recipient=post1.author,
        actor=user2,
        verb='like'
    ).first()
    
    if notification:
        print(f"✓ Notification created for {post1.author.username}")
        print(f"Notification message: {notification.message}")
    else:
        print("✗ No notification found")
    
    # Test 3: Try to create duplicate like (should fail with IntegrityError)
    print("\n--- Test 3: Testing unique constraint ---")
    try:
        Like.objects.create(user=user2, post=post1)
        print("✗ Duplicate like was created (should not happen)")
    except Exception as e:
        print(f"✓ Duplicate like prevented: {type(e).__name__}")
    
    # Test 4: Unlike the post
    print("\n--- Test 4: Unliking post ---")
    Like.objects.filter(user=user2, post=post1).delete()
    print(f"✓ {user2.username} unliked '{post1.title}'")
    print(f"Post like count after unlike: {post1.like_count}")
    print(f"Is liked by {user2.username}: {post1.is_liked_by(user2)}")
    
    # Test 5: Multiple users liking the same post
    print("\n--- Test 5: Multiple likes on same post ---")
    Like.objects.create(user=user1, post=post2)  # User1 likes User2's post
    Like.objects.create(user=user2, post=post2)  # User2 likes own post
    print(f"✓ Multiple users liked '{post2.title}'")
    print(f"Post like count: {post2.like_count}")
    
    # Test 6: Get recent likers
    print("\n--- Test 6: Recent likers ---")
    recent_likes = post2.likes.select_related('user').order_by('-created_at')[:5]
    recent_likers = [like.user.username for like in recent_likes]
    print(f"Recent likers of '{post2.title}': {recent_likers}")
    
    print("\n--- All tests completed! ---")

def test_models_are_working():
    """Basic test to ensure models are working"""
    print("Testing models...")
    
    # Test User model
    user_count = User.objects.count()
    print(f"Total users in database: {user_count}")
    
    # Test Post model
    post_count = Post.objects.count()
    print(f"Total posts in database: {post_count}")
    
    # Test Like model
    like_count = Like.objects.count()
    print(f"Total likes in database: {like_count}")
    
    # Test Notification model
    notification_count = Notification.objects.count()
    print(f"Total notifications in database: {notification_count}")
    
    print("✓ All models are accessible")

if __name__ == '__main__':
    try:
        test_models_are_working()
        test_like_functionality()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
