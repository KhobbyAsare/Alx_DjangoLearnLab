from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Tag
from django.utils.text import slugify


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        """Save method for updating user profile"""
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    """Form for creating and updating blog posts with tags"""
    title = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter post title',
            'maxlength': '200'
        })
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your post content here...',
            'rows': 8,
            'cols': 80
        })
    )
    tags_input = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g., python, web, django)',
            'data-toggle': 'tooltip',
            'title': 'Separate tags with commas. Tags will be created if they don\'t exist.'
        }),
        label='Tags',
        help_text='Enter tags separated by commas. New tags will be created automatically.'
    )

    class Meta:
        model = Post
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing post, populate the tags field
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def clean_tags_input(self):
        """Clean and validate tags input"""
        tags_input = self.cleaned_data.get('tags_input', '')
        if not tags_input.strip():
            return []
        
        # Split by comma and clean each tag
        tag_names = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
        
        # Validate tag names
        for tag_name in tag_names:
            if len(tag_name) > 50:
                raise forms.ValidationError(f'Tag "{tag_name}" is too long. Maximum length is 50 characters.')
            if not tag_name.replace('-', '').replace('_', '').isalnum():
                raise forms.ValidationError(f'Tag "{tag_name}" contains invalid characters. Use only letters, numbers, hyphens, and underscores.')
        
        # Remove duplicates while preserving order
        unique_tags = []
        for tag in tag_names:
            if tag not in unique_tags:
                unique_tags.append(tag)
                
        return unique_tags

    def save(self, commit=True):
        """Save method for creating/updating posts with tags"""
        post = super().save(commit=False)
        post.title = self.cleaned_data['title']
        post.content = self.cleaned_data['content']
        
        if commit:
            post.save()
            self.save_tags(post)
            
        return post
    
    def save_tags(self, post):
        """Save tags for the post"""
        tag_names = self.cleaned_data.get('tags_input', [])
        
        # Clear existing tags
        post.tags.clear()
        
        # Create or get tags and add them to the post
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            post.tags.add(tag)


class SearchForm(forms.Form):
    """Form for searching blog posts"""
    query = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts by title, content, or tags...',
            'autocomplete': 'off'
        }),
        label=''
    )
    
    def clean_query(self):
        """Clean and validate search query"""
        query = self.cleaned_data.get('query', '').strip()
        if len(query) < 2:
            raise forms.ValidationError('Search query must be at least 2 characters long.')
        return query


class CommentForm(forms.ModelForm):
    """Form for creating and updating comments"""
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control comment-textarea',
            'placeholder': 'Write your comment here...',
            'rows': 4,
            'cols': 50
        }),
        label='Comment'
    )

    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'style': 'resize: vertical; min-height: 100px;'
        })

    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data['content']
        if len(content.strip()) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters long.')
        if len(content) > 1000:
            raise forms.ValidationError('Comment cannot exceed 1000 characters.')
        return content.strip()

    def save(self, commit=True):
        """Save method for creating/updating comments"""
        comment = super().save(commit=False)
        comment.content = self.cleaned_data['content']
        if commit:
            comment.save()
        return comment
