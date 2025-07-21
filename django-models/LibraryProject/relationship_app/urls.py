# from django.urls import path

# from . import views

# app_name = 'relationship_app'

# urlpatterns = [
#     path('books/', views.list_books, name='list_books'),
#     path('library/<int:library_id>/', views.LibraryDetailView.as_view(), name='library_detail'),
# ]

from django.urls import path
from .views import list_books, LibraryDetailView, register, login, logout

app_name = 'relationship_app'

urlpatterns = [
    path('books/', list_books, name='list_books'),
    path('library/<int:library_id>/', LibraryDetailView.as_view(), name='library_detail'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]
