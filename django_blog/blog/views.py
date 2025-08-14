from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserProfileForm, PostForm, CommentForm, SearchForm
from .models import Post, Comment, Tag
from django.db.models import Q
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


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


@method_decorator(never_cache, name='dispatch')
class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure comments are filtered specifically for this post
        context['comments'] = self.object.comments.select_related('author').order_by('-created_at')
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


# ............CRUD FOR COMMENTS USING CBV

class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    """Create a new comment - class-based view approach"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/add_comment.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Get the post object and store it for later use"""
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add post to context"""
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        return context
    
    def form_valid(self, form):
        """Set the comment's post and author before saving"""
        form.instance.post = self.post
        form.instance.author = self.request.user
        messages.success(self.request, 'Your comment has been added successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        messages.error(self.request, 'Please correct the errors in your comment.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redirect to the post detail page after successful comment creation"""
        return reverse('post_detail', kwargs={'pk': self.post.pk})




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


# ............SEARCH AND TAG FUNCTIONALITY

def search_posts(request):
    """Search posts by title, content, or tags"""
    form = SearchForm()
    posts = []
    query = None
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Complex search using Q objects
            search_query = Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__name__icontains=query)
            posts = Post.objects.filter(search_query).distinct().order_by('-published_date')
    
    context = {
        'form': form,
        'posts': posts,
        'query': query,
        'total_results': posts.count() if posts else 0
    }
    
    return render(request, 'blog/search_results.html', context)


def posts_by_tag(request, slug):
    """Display posts filtered by a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.all().order_by('-published_date')
    
    context = {
        'tag': tag,
        'posts': posts,
        'total_posts': posts.count()
    }
    
    return render(request, 'blog/posts_by_tag.html', context)


class TagListView(generic.ListView):
    """Display all tags with post counts"""
    model = Tag
    template_name = 'blog/tag_list.html'
    context_object_name = 'tags'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_tags'] = Tag.objects.count()
        context['total_posts'] = Post.objects.count()
        return context


class PostListByTagView(generic.ListView):
    """Alternative class-based view for posts by tag"""
    model = Post
    template_name = 'blog/posts_by_tag.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(tags=self.tag).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['total_posts'] = self.get_queryset().count()
        return context

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

