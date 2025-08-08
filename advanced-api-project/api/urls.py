from django.urls import path
from .views import (
    BookListAPI,
    BookDetailAPI,
    BookCreateAPI,
    BookUpdateAPI,
    BookDeleteAPI
)

urlpatterns = [
    path('books/', BookListAPI.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailAPI.as_view(), name='book-detail'),
    path('books/create/', BookCreateAPI.as_view(), name='book-create'),
    path('books/<int:pk>/update/', BookUpdateAPI.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', BookDeleteAPI.as_view(), name='book-delete'),
]
