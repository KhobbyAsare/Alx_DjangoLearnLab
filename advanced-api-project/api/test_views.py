from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Author, Book
from datetime import date, timedelta

class BookAPITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create test author
        self.author = Author.objects.create(name='Test Author')
        
        # Create test books
        self.book1 = Book.objects.create(
            title='Book 1',
            publication_year=date(2020, 1, 1),
            author=self.author
        )
        self.book2 = Book.objects.create(
            title='Book 2',
            publication_year=date(2018, 1, 1),
            author=self.author
        )
        
        # URLs
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        self.create_url = reverse('book-create')
        self.update_url = reverse('book-update', kwargs={'pk': self.book1.pk})
        self.delete_url = reverse('book-delete', kwargs={'pk': self.book1.pk})

    def test_list_books_unauthenticated(self):
        """Test that unauthenticated users can list books"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_books_authenticated(self):
        """Test that authenticated users can list books"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_books_by_title(self):
        """Test filtering books by title"""
        response = self.client.get(self.list_url, {'title': 'Book 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Book 1')
    
    def test_search_books(self):
        """Test searching books by title"""
        response = self.client.get(self.list_url, {'search': 'Book'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_order_books_by_title(self):
        """Test ordering books by title"""
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Book 1')
        self.assertEqual(response.data[1]['title'], 'Book 2')
    
    def test_order_books_by_publication_year(self):
        """Test ordering books by publication year"""
        response = self.client.get(self.list_url, {'ordering': '-publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Book 1')
        self.assertEqual(response.data[1]['title'], 'Book 2')
    
    def test_retrieve_book_detail_unauthenticated(self):
        """Test that unauthenticated users can retrieve book details"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book 1')
    
    def test_retrieve_book_detail_authenticated(self):
        """Test that authenticated users can retrieve book details"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book 1')
    
    def test_create_book_unauthenticated(self):
        """Test that unauthenticated users cannot create books"""
        data = {
            'title': 'New Book',
            'publication_year': '2022-01-01',
            'author': self.author.pk
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated(self):
        """Test that authenticated users can create books"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Book',
            'publication_year': '2022-01-01',
            'author': self.author.pk
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.last().title, 'New Book')
    
    def test_create_book_with_future_publication_year(self):
        """Test that books with future publication years are rejected"""
        self.client.force_authenticate(user=self.user)
        future_date = date.today() + timedelta(days=365)
        data = {
            'title': 'Future Book',
            'publication_year': future_date.strftime('%Y-%m-%d'),
            'author': self.author.pk
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Publication year cannot be in the future', str(response.data))
    
    def test_update_book_unauthenticated(self):
        """Test that unauthenticated users cannot update books"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated(self):
        """Test that authenticated users can update books"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')
    
    def test_delete_book_unauthenticated(self):
        """Test that unauthenticated users cannot delete books"""
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book1.pk).exists())
    
    def test_delete_book_authenticated(self):
        """Test that authenticated users can delete books"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book1.pk).exists())