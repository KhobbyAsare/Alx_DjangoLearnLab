from django.shortcuts import render
from django.views.generic.detail import DetailView
from .models import Library, Book

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})


# Class-based view for displaying a library's detail and its books
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    pk_url_kwarg = 'library_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all books associated with this library
        context['books'] = self.object.books.all()
        return context

# Authentication views
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registering
            return redirect('relationship_app:list_books')  # Redirect wherever you want
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

# Login view
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('relationship_app:list_books')  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, 'relationship_app/login.html', {'form': form})

# Logout view
def logout(request):
    auth_logout(request)
    return redirect('relationship_app:login')  # Redirect after logout
