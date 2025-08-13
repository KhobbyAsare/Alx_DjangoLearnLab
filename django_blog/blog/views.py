from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User

# Login
class CustomLoginView(LoginView):
    template_name = 'blog/auth/login.html'
    redirect_authenticated_user = True

# Logout
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

# Register
class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'blog/auth/register.html'
    success_url = reverse_lazy('login')

# Profile (edit)
class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/auth/profile.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user
