#!/usr/bin/env python
"""
Debug script to check comment associations
Run this to check if comments are properly linked to posts
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')
django.setup()

from blog.models import Post, Comment

def debug_comments():
    print("=== COMMENT DEBUG REPORT ===")
    print()
    
    # Get all posts
    posts = Post.objects.all().prefetch_related('comments__author')
    
    if not posts:
        print("❌ No posts found in database")
        return
    
    print(f"📝 Found {posts.count()} posts")
    print()
    
    for post in posts:
        print(f"Post ID: {post.pk}")
        print(f"Title: {post.title}")
        print(f"Author: {post.author.username}")
        print(f"Comments: {post.comments.count()}")
        
        if post.comments.exists():
            print("   Comments for this post:")
            for comment in post.comments.all():
                print(f"   - ID: {comment.pk}, Author: {comment.author.username}")
                print(f"     Content: {comment.content[:50]}...")
                print(f"     Post ID: {comment.post.pk} (should match {post.pk})")
                if comment.post.pk != post.pk:
                    print(f"   ⚠️  MISMATCH! Comment linked to post {comment.post.pk} but showing on post {post.pk}")
        else:
            print("   No comments")
        
        print("-" * 50)
        print()
    
    # Check all comments
    print("=== ALL COMMENTS IN DATABASE ===")
    comments = Comment.objects.all().select_related('post', 'author')
    
    for comment in comments:
        print(f"Comment ID: {comment.pk}")
        print(f"Author: {comment.author.username}")
        print(f"Post: {comment.post.title} (ID: {comment.post.pk})")
        print(f"Content: {comment.content[:50]}...")
        print("-" * 30)

if __name__ == "__main__":
    debug_comments()
