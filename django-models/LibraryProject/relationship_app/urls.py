# from django.urls import path

# from . import views

# app_name = 'relationship_app'

# urlpatterns = [
#     path('books/', views.list_books, name='list_books'),
#     path('library/<int:library_id>/', views.LibraryDetailView.as_view(), name='library_detail'),
# ]

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'relationship_app'

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:library_id>/', views.LibraryDetailView.as_view(), name='library_detail'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('admin-dashboard/', views.admin_view, name='admin_view'),
    path('librarian-dashboard/', views.librarian_view, name='librarian_view'),
    path('member-dashboard/', views.member_view, name='member_view'),
]
