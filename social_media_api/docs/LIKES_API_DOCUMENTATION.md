# Likes API Documentation

This document describes the like functionality implemented in the social media API.

## Overview

The likes system allows authenticated users to like and unlike posts, with automatic notification generation and comprehensive like management features.

## Models

### Like Model
Located in `posts/models.py`

```python
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']  # Ensures one like per user per post
```

### Post Model Extensions
The Post model includes like-related methods:
- `like_count` property: Returns total number of likes
- `is_liked_by(user)` method: Checks if a specific user has liked the post

## API Endpoints

All endpoints require authentication (`IsAuthenticated` permission).

### Like a Post
**POST** `/api/posts/{post_id}/like/`

Like a specific post. Creates a notification for the post author.

**Response (201 Created):**
```json
{
    "message": "You liked \"Post Title\"",
    "liked": true,
    "post_info": {
        "id": 1,
        "title": "Post Title",
        "like_count": 5,
        "is_liked_by_user": true,
        "recent_likes": ["user1", "user2", "user3"]
    }
}
```

**Error (400 Bad Request):**
```json
{
    "error": "You have already liked this post",
    "liked": true
}
```

### Unlike a Post
**POST** `/api/posts/{post_id}/unlike/`

Remove like from a specific post. Deletes related notification.

**Response (200 OK):**
```json
{
    "message": "You unliked \"Post Title\"",
    "liked": false,
    "post_info": {
        "id": 1,
        "title": "Post Title",
        "like_count": 4,
        "is_liked_by_user": false,
        "recent_likes": ["user2", "user3", "user4"]
    }
}
```

### Toggle Like
**POST** `/api/posts/{post_id}/toggle-like/`

Toggle like status. If liked, unlikes; if not liked, likes.

**Response (Like created - 201 Created):**
```json
{
    "message": "You liked \"Post Title\"",
    "liked": true,
    "post_info": { ... }
}
```

**Response (Like removed - 200 OK):**
```json
{
    "message": "You unliked \"Post Title\"",
    "liked": false,
    "post_info": { ... }
}
```

### Get Post Like Info
**GET** `/api/posts/{post_id}/like-info/`

Get detailed like information for a post.

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Post Title",
    "like_count": 5,
    "is_liked_by_user": true,
    "recent_likes": ["user1", "user2", "user3", "user4", "user5"]
}
```

### List Post Likes
**GET** `/api/posts/{post_id}/likes/`

Get list of all users who liked a specific post.

**Response (200 OK):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": "username1",
            "post": 1,
            "post_title": "Post Title",
            "created_at": "2025-08-21T10:30:00Z"
        },
        {
            "id": 2,
            "user": "username2",
            "post": 1,
            "post_title": "Post Title", 
            "created_at": "2025-08-21T09:15:00Z"
        }
    ]
}
```

### My Likes
**GET** `/api/my-likes/`

Get list of all posts liked by the current user.

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": "current_user",
            "post": 1,
            "post_title": "Post Title 1",
            "created_at": "2025-08-21T10:30:00Z"
        },
        {
            "id": 2,
            "user": "current_user",
            "post": 5,
            "post_title": "Post Title 5",
            "created_at": "2025-08-21T09:15:00Z"
        }
    ]
}
```

### Batch Like Actions
**POST** `/api/batch-like/`

Perform multiple like/unlike actions in a single request.

**Request Body:**
```json
[
    {
        "post_id": 1,
        "action": "like"
    },
    {
        "post_id": 2,
        "action": "unlike"
    },
    {
        "post_id": 3,
        "action": "like"
    }
]
```

**Response (200 OK):**
```json
{
    "results": [
        {
            "post_id": 1,
            "action": "liked",
            "success": true
        },
        {
            "post_id": 2,
            "action": "unliked", 
            "success": true
        },
        {
            "post_id": 3,
            "action": "already_liked",
            "success": false,
            "error": "Already liked"
        }
    ],
    "success_count": 2,
    "error_count": 1
}
```

## Serializers

### LikeSerializer
Serializes Like model instances with user and post information.

### PostLikeInfoSerializer  
Provides comprehensive like information for posts including:
- Total like count
- Whether current user has liked
- Recent likers list (up to 5 most recent)

### LikeActionSerializer
Validates like/unlike actions for both single and batch operations.

## Features

### Automatic Notifications
- When a user likes a post, a notification is automatically sent to the post author
- When a user unlikes a post, the related notification is removed
- Users don't receive notifications for liking their own posts

### Race Condition Protection
- Uses database constraints to prevent duplicate likes
- Handles race conditions gracefully with try/catch blocks
- Returns appropriate error messages for duplicate actions

### Performance Optimizations
- Uses `select_related()` for efficient database queries
- Implements pagination for like lists
- Caches like counts using database properties

### Security
- All endpoints require authentication
- Only published posts can be liked
- Users can only like posts once
- Proper permission checks on all operations

## Error Handling

Common error responses:

**Post Not Found (404):**
```json
{
    "detail": "Not found."
}
```

**Already Liked (400):**
```json
{
    "error": "You have already liked this post",
    "liked": true
}
```

**Not Previously Liked (400):**
```json
{
    "error": "You have not liked this post",
    "liked": false
}
```

**Unpublished Post (404):**
Posts that are not published (`is_published=False`) will return 404 Not Found.

## Database Schema

### Likes Table
```sql
CREATE TABLE posts_like (
    id BIGINT PRIMARY KEY,
    post_id BIGINT REFERENCES posts_post(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(post_id, user_id)
);
```

### Indexes
- Primary key index on `id`
- Unique constraint index on `(post_id, user_id)`
- Foreign key indexes on `post_id` and `user_id`
- Index on `created_at` for ordering

## Testing

Run the test script to verify like functionality:

```bash
python test_likes.py
```

The test script verifies:
- Like creation and deletion
- Unique constraint enforcement
- Like counting
- User like checking
- Recent likers functionality

## Usage Examples

### Frontend Integration
```javascript
// Like a post
const likePost = async (postId) => {
    const response = await fetch(`/api/posts/${postId}/like/`, {
        method: 'POST',
        headers: {
            'Authorization': `Token ${userToken}`,
            'Content-Type': 'application/json'
        }
    });
    return response.json();
};

// Toggle like status
const toggleLike = async (postId) => {
    const response = await fetch(`/api/posts/${postId}/toggle-like/`, {
        method: 'POST',
        headers: {
            'Authorization': `Token ${userToken}`,
            'Content-Type': 'application/json'
        }
    });
    return response.json();
};

// Get like info
const getLikeInfo = async (postId) => {
    const response = await fetch(`/api/posts/${postId}/like-info/`, {
        headers: {
            'Authorization': `Token ${userToken}`
        }
    });
    return response.json();
};
```

## Migration Notes

The like functionality was added after initial migrations. If you encounter migration issues:

1. Ensure all apps are properly migrated
2. Check that `AUTH_USER_MODEL` is correctly set
3. Verify foreign key relationships are correct
4. Run `python manage.py check` to identify issues

## Future Enhancements

Potential improvements to consider:
- Like analytics and insights
- Like reaction types (love, laugh, etc.)
- Bulk like operations for administrators
- Like activity feeds
- Real-time like notifications via WebSockets
