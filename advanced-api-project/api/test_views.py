# api/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Book, Author
from datetime import date


class BookAPITestCase(APITestCase):
    """
    Unit test suite for the Book API endpoints.
    Covers:
    - CRUD operations
    - Filtering, searching, ordering
    - Authentication & permission checks
    """

    def setUp(self):
        """
        Set up the test environment.
        Creates a test user, authors, and sample books.
        """
        # Create user for authentication tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        # Create authors first
        self.author1 = Author.objects.create(name='Author A')
        self.author2 = Author.objects.create(name='Author B')

        # Create sample books with publication dates
        self.book1 = Book.objects.create(
            title='Book One',
            author=self.author1,
            publication_year=date(2020, 1, 1)
        )
        self.book2 = Book.objects.create(
            title='Book Two',
            author=self.author2,
            publication_year=date(2021, 1, 1)
        )

        # API endpoint URLs
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', args=[self.book1.id])

    def authenticate(self):
        """Helper to log in the test user."""
        self.client.force_authenticate(user=self.user)

    def test_list_books(self):
        """GET /books/ should return all books."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Book One')
        self.assertEqual(response.data[1]['title'], 'Book Two')

    def test_create_book_authenticated(self):
        """POST /books/ should create a book if authenticated."""
        self.authenticate()
        author_c = Author.objects.create(name='Author C')
        data = {
            'title': 'Book Three',
            'author': author_c.id,
            'publication_year': '2022-01-01'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.last().title, 'Book Three')

    def test_create_book_unauthenticated(self):
        """POST /books/ without login should be forbidden."""
        author_d = Author.objects.create(name='Author D')
        data = {
            'title': 'Book Four',
            'author': author_d.id,
            'publication_year': '2023-01-01'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_single_book(self):
        """GET /books/<id>/ should return that book."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book One')
        self.assertEqual(response.data['author']['name'], 'Author A')

    def test_update_book_authenticated(self):
        """PUT /books/<id>/ should update a book if authenticated."""
        self.authenticate()
        data = {
            'title': 'Updated Book One',
            'author': self.author1.id,
            'publication_year': '2020-01-01'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Book One')

    def test_update_book_unauthenticated(self):
        """PUT /books/<id>/ without login should be forbidden."""
        data = {
            'title': 'No Auth Update',
            'author': self.author1.id,
            'publication_year': '2020-01-01'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_authenticated(self):
        """DELETE /books/<id>/ should remove a book if authenticated."""
        self.authenticate()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())

    def test_delete_book_unauthenticated(self):
        """DELETE /books/<id>/ without login should be forbidden."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 2)

    def test_filter_books_by_author(self):
        """GET /books/?author=<id> should return matching books."""
        response = self.client.get(self.list_url, {'author': self.author1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author']['name'], 'Author A')

    def test_search_books_by_title(self):
        """GET /books/?search=<title> should return matching books."""
        response = self.client.get(self.list_url, {'search': 'Book One'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Book One')

    def test_order_books_by_publication_year(self):
        """GET /books/?ordering=publication_year should return books sorted by year."""
        response = self.client.get(self.list_url, {'ordering': 'publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data]
        self.assertEqual(titles, ['Book One', 'Book Two'])