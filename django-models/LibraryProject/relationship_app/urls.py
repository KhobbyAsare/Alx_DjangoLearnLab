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
    # VIEWS FOR ALL USERS
    path('books/', views.list_books, name='list_books'),
    path('library/<int:library_id>/', views.LibraryDetailView.as_view(), name='library_detail'),
    # AUTHENTICATION
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    # DASHBOARD BASE ON ROLES
    path('admin-dashboard/', views.admin_view, name='admin_view'),
    path('librarian-dashboard/', views.librarian_view, name='librarian_view'),
    path('member-dashboard/', views.member_view, name='member_view'),
    # PERMISSIONS FOR THE ROLES OF USERS
    path('books/add_book/', views.add_book, name='add_book'),
    path('books/edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
]
