# api/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Book, Author
from datetime import date


class BookAPITestCase(APITestCase):
    """
    Comprehensive test suite for Book API endpoints.
    Uses Django's test database to avoid impacting production data.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase (runs once).
        This data will be available for all tests but won't be modified.
        """
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create authors
        cls.author1 = Author.objects.create(name='J.K. Rowling')
        cls.author2 = Author.objects.create(name='George R.R. Martin')

    def setUp(self):
        """
        Set up data for each individual test (runs before each test).
        These objects will be recreated for each test method.
        """
        # Create test books
        self.book1 = Book.objects.create(
            title='Harry Potter',
            author=self.author1,
            publication_year=date(1997, 6, 26)
        )
        self.book2 = Book.objects.create(
            title='A Game of Thrones',
            author=self.author2,
            publication_year=date(1996, 8, 1)
        )
        
        # Set up API endpoints
        self.list_url = reverse('book-list')  # '/api/books/'
        self.detail_url = reverse('book-detail', kwargs={'pk': self.book1.pk})  # '/api/books/1/'

    def authenticate_user(self):
        """Helper method to authenticate the test user for protected endpoints"""
        self.client.force_authenticate(user=self.user)

    # Authentication Tests
    def test_unauthenticated_access_to_protected_endpoints(self):
        """Verify unauthenticated users cannot access protected endpoints"""
        endpoints = [
            (self.client.post, self.list_url, {'title': 'New Book', 'author': self.author1.id}),
            (self.client.put, self.detail_url, {'title': 'Updated Title', 'author': self.author1.id}),
            (self.client.delete, self.detail_url, None)
        ]
        
        for method, url, data in endpoints:
            response = method(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # CRUD Operation Tests
    def test_list_books(self):
        """GET /books/ should return all books with correct structure"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify response structure
        for book in response.data:
            self.assertIn('id', book)
            self.assertIn('title', book)
            self.assertIn('author', book)
            self.assertIn('publication_year', book)

    def test_retrieve_single_book(self):
        """GET /books/<id>/ should return the requested book"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Harry Potter')
        self.assertEqual(response.data['author'], self.author1.id)

    def test_create_book_authenticated(self):
        """POST /books/ should create a new book when authenticated"""
        self.authenticate_user()
        new_book_data = {
            'title': 'The Hobbit',
            'author': self.author1.id,
            'publication_year': '1937-09-21'
        }
        
        response = self.client.post(self.list_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.latest('id').title, 'The Hobbit')

    def test_update_book_authenticated(self):
        """PUT /books/<id>/ should update an existing book when authenticated"""
        self.authenticate_user()
        updated_data = {
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'author': self.author1.id,
            'publication_year': '1997-06-26'
        }
        
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, updated_data['title'])

    def test_delete_book_authenticated(self):
        """DELETE /books/<id>/ should remove the book when authenticated"""
        self.authenticate_user()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(Book.objects.filter(pk=self.book1.pk).exists())

    # Filtering and Ordering Tests
    def test_filter_books_by_author(self):
        """GET /books/?author=<id> should return books by specified author"""
        response = self.client.get(self.list_url, {'author': self.author1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author'], self.author1.id)

    def test_order_books_by_publication_year(self):
        """GET /books/?ordering=publication_year should return ordered results"""
        response = self.client.get(self.list_url, {'ordering': 'publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        publication_years = [book['publication_year'] for book in response.data]
        self.assertEqual(publication_years, sorted(publication_years))

    def test_order_books_by_title(self):
        """GET /books/?ordering=title should return alphabetically ordered results"""
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data]
        self.assertEqual(titles, sorted(titles))

    # Validation Tests
    def test_create_book_invalid_data(self):
        """POST /books/ should reject invalid data with proper errors"""
        self.authenticate_user()
        invalid_data = [
            ({}, 'empty data'),
            ({'title': ''}, 'empty title'),
            ({'title': 'No Author'}, 'missing author'),
            ({'title': 'Bad Date', 'author': self.author1.id, 'publication_year': 'invalid-date'}, 'invalid date')
        ]
        
        for data, description in invalid_data:
            with self.subTest(description=description):
                response = self.client.post(self.list_url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('errors', str(response.data))

    def tearDown(self):
        """Clean up after each test"""
        # Explicitly clear authentication
        self.client.force_authenticate(user=None)
        # Django automatically handles test database cleanup