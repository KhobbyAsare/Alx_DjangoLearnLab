from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserProfileForm, PostForm, CommentForm
from .models import Post, Comment
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse


def home(request):
    """Home page view"""
    return render(request, 'blog/home.html')


def login_view(request):
    """Login view with POST method handling"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/login.html', {'form': form})


def register_view(request):
    """Register view with POST method handling and save() functionality"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'blog/register.html', {'form': form})


@login_required
def profile_view(request):
    """Profile view with POST method handling and save() functionality"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            # Save the updated user profile
            user = form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'blog/profile.html', {'form': form})


@login_required
def edit_profile_view(request):
    """Edit profile view with POST method handling and save() functionality"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            # Save the updated user profile
            user = form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# ............CRUD FOR THE POST USING CBV

class PostListView(generic.ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 10


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['comment_form'] = CommentForm()
        context['comment_count'] = self.object.comments.count()
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment form submission"""
        self.object = self.get_object()
        
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to comment.')
            return redirect('login')
        
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            return HttpResponseRedirect(reverse('post_detail', args=[self.object.pk]))
        else:
            messages.error(request, 'Please correct the errors in your comment.')
            
        # If form is invalid, redisplay the page with errors
        context = self.get_context_data()
        context['comment_form'] = comment_form
        return render(request, self.template_name, context)


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')
    
    def test_func(self):
        """Test if the current user is the author of the post"""
        post = self.get_object()
        return post.author == self.request.user
    
    def handle_no_permission(self):
        """Handle case when user doesn't have permission"""
        messages.error(self.request, 'You can only edit your own posts.')
        return redirect('post_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')
    context_object_name = 'post'
    
    def test_func(self):
        """Test if the current user is the author of the post"""
        post = self.get_object()
        return post.author == self.request.user
    
    def handle_no_permission(self):
        """Handle case when user doesn't have permission"""
        messages.error(self.request, 'You can only delete your own posts.')
        return redirect('post_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ............CRUD FOR COMMENTS USING CBV AND FBV

@login_required
def add_comment(request, post_id):
    """Add a new comment to a post"""
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            return HttpResponseRedirect(reverse('post_detail', args=[post_id]))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CommentForm()
    
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/add_comment.html', context)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """Update a comment - only by the comment author"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/edit_comment.html'
    context_object_name = 'comment'
    
    def test_func(self):
        """Test if the current user is the author of the comment"""
        comment = self.get_object()
        return comment.author == self.request.user
    
    def handle_no_permission(self):
        """Handle case when user doesn't have permission"""
        messages.error(self.request, 'You can only edit your own comments.')
        comment = self.get_object()
        return redirect('post_detail', pk=comment.post.pk)
    
    def form_valid(self, form):
        messages.success(self.request, 'Comment updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """Delete a comment - only by the comment author"""
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    context_object_name = 'comment'
    
    def test_func(self):
        """Test if the current user is the author of the comment"""
        comment = self.get_object()
        return comment.author == self.request.user
    
    def handle_no_permission(self):
        """Handle case when user doesn't have permission"""
        messages.error(self.request, 'You can only delete your own comments.')
        comment = self.get_object()
        return redirect('post_detail', pk=comment.post.pk)
    
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        post_pk = comment.post.pk
        messages.success(request, 'Comment deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})


# Function-based view to display post with comments and comment form
def post_detail_with_comments(request, pk):
    """Display post with comments and handle comment form submission"""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            return HttpResponseRedirect(reverse('post_detail', args=[pk]))
        else:
            messages.error(request, 'Please correct the errors in your comment.')
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'comment_count': comments.count()
    }
    return render(request, 'blog/post_detail.html', context)
