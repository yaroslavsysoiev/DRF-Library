"""
Tests for Books app.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestBookList:
    """Test book list functionality."""
    
    def test_book_list_success(self, api_client, multiple_books):
        """Test successful book list retrieval."""
        url = reverse('books:book-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
    
    def test_book_list_filter_by_author(self, api_client, multiple_books):
        """Test book list filtering by author."""
        url = reverse('books:book-list')
        author = multiple_books[0].author
        
        response = api_client.get(url, {'author': author})
        
        assert response.status_code == status.HTTP_200_OK
        for book in response.data['results']:
            assert book['author'] == author
    
    def test_book_list_search_by_title(self, api_client, multiple_books):
        """Test book list search by title."""
        url = reverse('books:book-list')
        search_term = multiple_books[0].title.split()[0]
        
        response = api_client.get(url, {'search': search_term})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_book_list_ordering_by_title(self, api_client, multiple_books):
        """Test book list ordering by title."""
        url = reverse('books:book-list')
        
        response = api_client.get(url, {'ordering': 'title'})
        
        assert response.status_code == status.HTTP_200_OK
        titles = [book['title'] for book in response.data['results']]
        assert titles == sorted(titles)
    
    def test_book_list_ordering_by_daily_fee_desc(self, api_client, multiple_books):
        """Test book list ordering by daily fee descending."""
        url = reverse('books:book-list')
        
        response = api_client.get(url, {'ordering': '-daily_fee'})
        
        assert response.status_code == status.HTTP_200_OK
        fees = [book['daily_fee'] for book in response.data['results']]
        assert fees == sorted(fees, reverse=True)


@pytest.mark.django_db
class TestBookDetail:
    """Test book detail functionality."""
    
    def test_book_detail_success(self, api_client, book):
        """Test successful book detail retrieval."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == book.id
        assert response.data['title'] == book.title
        assert response.data['author'] == book.author
        assert response.data['cover'] == book.cover
        assert response.data['inventory'] == book.inventory
        assert response.data['daily_fee'] == str(book.daily_fee)
    
    def test_book_detail_not_found(self, api_client):
        """Test book detail with non-existent book."""
        url = reverse('books:book-detail', kwargs={'pk': 99999})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookCreate:
    """Test book creation functionality."""
    
    def test_book_create_admin_success(self, admin_client):
        """Test successful book creation by admin."""
        url = reverse('books:book-list')
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'cover': 'HARD',
            'inventory': 5,
            'daily_fee': '10.50'
        }
        
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test Book'
        assert response.data['author'] == 'Test Author'
        assert response.data['cover'] == 'HARD'
        assert response.data['inventory'] == 5
        assert response.data['daily_fee'] == '10.50'
    
    def test_book_create_unauthorized(self, auth_client):
        """Test book creation by non-admin user."""
        url = reverse('books:book-list')
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'cover': 'HARD',
            'inventory': 5,
            'daily_fee': '10.50'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_book_create_invalid_data(self, admin_client):
        """Test book creation with invalid data."""
        url = reverse('books:book-list')
        data = {
            'title': '',  # Empty title
            'author': 'Test Author',
            'cover': 'INVALID',  # Invalid cover
            'inventory': -1,  # Negative inventory
            'daily_fee': '-10.50'  # Negative fee
        }
        
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'cover' in response.data
        assert 'inventory' in response.data
        assert 'daily_fee' in response.data


@pytest.mark.django_db
class TestBookUpdate:
    """Test book update functionality."""
    
    def test_book_update_admin_success(self, admin_client, book):
        """Test successful book update by admin."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        data = {
            'title': 'Updated Book Title',
            'daily_fee': '15.75'
        }
        
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Book Title'
        assert response.data['daily_fee'] == '15.75'
    
    def test_book_update_unauthorized(self, auth_client, book):
        """Test book update by non-admin user."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        data = {
            'title': 'Updated Book Title'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_book_update_invalid_data(self, admin_client, book):
        """Test book update with invalid data."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        data = {
            'inventory': -5,  # Negative inventory
            'daily_fee': '-5.00'  # Negative fee
        }
        
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'inventory' in response.data
        assert 'daily_fee' in response.data


@pytest.mark.django_db
class TestBookDelete:
    """Test book deletion functionality."""
    
    def test_book_delete_admin_success(self, admin_client, book):
        """Test successful book deletion by admin."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_book_delete_unauthorized(self, auth_client, book):
        """Test book deletion by non-admin user."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookModel:
    """Test Book model functionality."""
    
    def test_book_creation(self):
        """Test book creation."""
        from books.models import Book
        
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            cover='HARD',
            inventory=5,
            daily_fee=10.50
        )
        
        assert book.title == 'Test Book'
        assert book.author == 'Test Author'
        assert book.cover == 'HARD'
        assert book.inventory == 5
        assert book.daily_fee == 10.50
        assert book.is_available is True
    
    def test_book_str_representation(self, book):
        """Test book string representation."""
        expected = f"{book.title} by {book.author}"
        assert str(book) == expected
    
    def test_book_is_available_true(self, book):
        """Test book availability when inventory > 0."""
        book.inventory = 5
        book.save()
        assert book.is_available is True
    
    def test_book_is_available_false(self, book):
        """Test book availability when inventory = 0."""
        book.inventory = 0
        book.save()
        assert book.is_available is False
    
    def test_book_cover_choices(self):
        """Test book cover choices."""
        from books.models import Book
        
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            cover='HARD',
            inventory=1,
            daily_fee=10.00
        )
        
        cover_choices = [choice[0] for choice in Book.COVER_CHOICES]
        assert book.cover in cover_choices


@pytest.mark.django_db
class TestBookSerializers:
    """Test book serializers."""
    
    def test_book_serializer_valid_data(self):
        """Test BookSerializer with valid data."""
        from books.serializers import BookSerializer
        
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'cover': 'HARD',
            'inventory': 5,
            'daily_fee': '10.50'
        }
        
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()
    
    def test_book_serializer_invalid_data(self):
        """Test BookSerializer with invalid data."""
        from books.serializers import BookSerializer
        
        data = {
            'title': '',  # Empty title
            'author': 'Test Author',
            'cover': 'INVALID',  # Invalid cover
            'inventory': -1,  # Negative inventory
            'daily_fee': '-10.50'  # Negative fee
        }
        
        serializer = BookSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
        assert 'cover' in serializer.errors
        assert 'inventory' in serializer.errors
        assert 'daily_fee' in serializer.errors
    
    def test_book_list_serializer(self, book):
        """Test BookListSerializer."""
        from books.serializers import BookListSerializer
        
        serializer = BookListSerializer(book)
        data = serializer.data
        
        assert data['id'] == book.id
        assert data['title'] == book.title
        assert data['author'] == book.author
        assert data['cover'] == book.cover
        assert data['inventory'] == book.inventory
        assert data['daily_fee'] == str(book.daily_fee)
        assert 'is_available' in data


@pytest.mark.django_db
class TestBookPermissions:
    """Test book permissions."""
    
    def test_book_list_permission_public(self, api_client):
        """Test that book list is publicly accessible."""
        url = reverse('books:book-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_book_detail_permission_public(self, api_client, book):
        """Test that book detail is publicly accessible."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_book_create_permission_admin_only(self, auth_client):
        """Test that book creation requires admin permissions."""
        url = reverse('books:book-list')
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'cover': 'HARD',
            'inventory': 5,
            'daily_fee': '10.50'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_book_update_permission_admin_only(self, auth_client, book):
        """Test that book update requires admin permissions."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        data = {
            'title': 'Updated Title'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_book_delete_permission_admin_only(self, auth_client, book):
        """Test that book deletion requires admin permissions."""
        url = reverse('books:book-detail', kwargs={'pk': book.pk})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN