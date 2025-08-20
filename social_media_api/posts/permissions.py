from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Read permissions are allowed to any authenticated user.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            # Only allow reading published posts
            if hasattr(obj, 'is_published'):
                return obj.is_published or obj.author == request.user
            # For comments, check if the parent post is published
            elif hasattr(obj, 'post'):
                return obj.post.is_published or obj.post.author == request.user
            return True
        
        # Write permissions are only allowed to the author of the object
        return obj.author == request.user


class IsAuthorOrReadOnlyForComments(permissions.BasePermission):
    """
    Custom permission specifically for comments
    """
    
    def has_permission(self, request, view):
        # All authenticated users can read and create comments
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for comment author
        return obj.author == request.user


class CanCommentOnPost(permissions.BasePermission):
    """
    Permission to check if user can comment on a post
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can comment on published posts
        if hasattr(obj, 'is_published'):
            return obj.is_published
        return True
