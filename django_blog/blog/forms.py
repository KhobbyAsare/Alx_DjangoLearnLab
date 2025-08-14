from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Tag
from django.utils.text import slugify
from taggit.forms import TagWidget


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
    """Form for creating and updating blog posts with django-taggit"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'taggit_tags']
        widgets = {
            'taggit_tags': TagWidget(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas',
                'data-toggle': 'tooltip',
                'title': 'Separate tags with commas. Tags will be created automatically.'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['taggit_tags'].label = "Tags"
        self.fields['taggit_tags'].help_text = "Enter tags separated by commas. New tags will be created automatically."


class TaggitPostForm(forms.ModelForm):
    """Alternative form using django-taggit's TagWidget"""
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
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'taggit_tags']
        widgets = {
            'taggit_tags': TagWidget(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas',
                'data-toggle': 'tooltip',
                'title': 'Separate tags with commas. Tags will be created automatically.'
            })
        }


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
