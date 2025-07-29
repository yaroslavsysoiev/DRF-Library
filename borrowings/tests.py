"""
Tests for Borrowings app.
"""

import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestBorrowingList:
    """Test borrowing list functionality."""
    
    def test_borrowing_list_user_success(self, auth_client, user, multiple_borrowings):
        """Test successful borrowing list retrieval for user."""
        url = reverse('borrowings:borrowing-list')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        # User should only see their own borrowings
        for borrowing in response.data['results']:
            assert borrowing['user'] == user.id
    
    def test_borrowing_list_admin_all_borrowings(self, admin_client, multiple_borrowings):
        """Test admin can see all borrowings."""
        url = reverse('borrowings:borrowing-list')
        
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(multiple_borrowings)
    
    def test_borrowing_list_filter_by_is_active(self, auth_client, user, borrowing, returned_borrowing):
        """Test borrowing list filtering by is_active."""
        url = reverse('borrowings:borrowing-list')
        
        response = auth_client.get(url, {'is_active': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        for borrowing_data in response.data['results']:
            assert borrowing_data['is_active'] is True
    
    def test_borrowing_list_filter_by_user_id_admin(self, admin_client, user, borrowing):
        """Test admin filtering borrowings by user_id."""
        url = reverse('borrowings:borrowing-list')
        
        response = admin_client.get(url, {'user_id': user.id})
        
        assert response.status_code == status.HTTP_200_OK
        for borrowing_data in response.data['results']:
            assert borrowing_data['user'] == user.id
    
    def test_borrowing_list_unauthorized(self, api_client):
        """Test borrowing list without authentication."""
        url = reverse('borrowings:borrowing-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBorrowingDetail:
    """Test borrowing detail functionality."""
    
    def test_borrowing_detail_user_success(self, auth_client, user, borrowing):
        """Test successful borrowing detail retrieval for user."""
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': borrowing.pk})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == borrowing.id
        assert response.data['user'] == user.id
        assert response.data['book'] == borrowing.book.id
    
    def test_borrowing_detail_admin_success(self, admin_client, borrowing):
        """Test successful borrowing detail retrieval for admin."""
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': borrowing.pk})
        
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == borrowing.id
    
    def test_borrowing_detail_unauthorized(self, api_client, borrowing):
        """Test borrowing detail without authentication."""
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': borrowing.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_borrowing_detail_not_found(self, auth_client):
        """Test borrowing detail with non-existent borrowing."""
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': 99999})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_borrowing_detail_wrong_user(self, auth_client, borrowing, multiple_users):
        """Test user cannot access another user's borrowing."""
        other_user = multiple_users[0]
        borrowing.user = other_user
        borrowing.save()
        
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': borrowing.pk})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBorrowingCreate:
    """Test borrowing creation functionality."""
    
    def test_borrowing_create_success(self, auth_client, user, book):
        """Test successful borrowing creation."""
        url = reverse('borrowings:borrowing-list')
        data = {
            'book': book.id,
            'expected_return_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == user.id
        assert response.data['book'] == book.id
        assert response.data['is_active'] is True
    
    def test_borrowing_create_unavailable_book(self, auth_client, book):
        """Test borrowing creation with unavailable book."""
        book.inventory = 0
        book.save()
        
        url = reverse('borrowings:borrowing-list')
        data = {
            'book': book.id,
            'expected_return_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'book' in response.data
    
    def test_borrowing_create_invalid_dates(self, auth_client, book):
        """Test borrowing creation with invalid dates."""
        url = reverse('borrowings:borrowing-list')
        data = {
            'book': book.id,
            'expected_return_date': (date.today() - timedelta(days=1)).isoformat()
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'expected_return_date' in response.data
    
    def test_borrowing_create_unauthorized(self, api_client, book):
        """Test borrowing creation without authentication."""
        url = reverse('borrowings:borrowing-list')
        data = {
            'book': book.id,
            'expected_return_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBorrowingReturn:
    """Test borrowing return functionality."""
    
    def test_borrowing_return_success(self, auth_client, borrowing):
        """Test successful borrowing return."""
        url = reverse('borrowings:borrowing-return', kwargs={'pk': borrowing.pk})
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is False
        assert response.data['actual_return_date'] == date.today().isoformat()
    
    def test_borrowing_return_already_returned(self, auth_client, returned_borrowing):
        """Test returning an already returned borrowing."""
        url = reverse('borrowings:borrowing-return', kwargs={'pk': returned_borrowing.pk})
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'actual_return_date' in response.data
    
    def test_borrowing_return_wrong_user(self, auth_client, borrowing, multiple_users):
        """Test user cannot return another user's borrowing."""
        other_user = multiple_users[0]
        borrowing.user = other_user
        borrowing.save()
        
        url = reverse('borrowings:borrowing-return', kwargs={'pk': borrowing.pk})
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_borrowing_return_unauthorized(self, api_client, borrowing):
        """Test borrowing return without authentication."""
        url = reverse('borrowings:borrowing-return', kwargs={'pk': borrowing.pk})
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBorrowingModel:
    """Test Borrowing model functionality."""
    
    def test_borrowing_creation(self, user, book):
        """Test borrowing creation."""
        from borrowings.models import Borrowing
        
        borrowing = Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=14)
        )
        
        assert borrowing.user == user
        assert borrowing.book == book
        assert borrowing.borrow_date == date.today()
        assert borrowing.expected_return_date == date.today() + timedelta(days=14)
        assert borrowing.actual_return_date is None
        assert borrowing.is_active is True
    
    def test_borrowing_str_representation(self, borrowing):
        """Test borrowing string representation."""
        expected = f"{borrowing.user.email} borrowed {borrowing.book.title}"
        assert str(borrowing) == expected
    
    def test_borrowing_is_active_true(self, borrowing):
        """Test borrowing is_active when not returned."""
        assert borrowing.is_active is True
    
    def test_borrowing_is_active_false(self, returned_borrowing):
        """Test borrowing is_active when returned."""
        assert returned_borrowing.is_active is False
    
    def test_borrowing_is_overdue_true(self, overdue_borrowing):
        """Test borrowing is_overdue when overdue."""
        assert overdue_borrowing.is_overdue is True
    
    def test_borrowing_is_overdue_false(self, borrowing):
        """Test borrowing is_overdue when not overdue."""
        assert borrowing.is_overdue is False
    
    def test_borrowing_overdue_days(self, overdue_borrowing):
        """Test borrowing overdue_days calculation."""
        assert overdue_borrowing.overdue_days > 0
    
    def test_borrowing_overdue_days_not_overdue(self, borrowing):
        """Test borrowing overdue_days when not overdue."""
        assert borrowing.overdue_days == 0
    
    def test_borrowing_save_decreases_inventory(self, user, book):
        """Test that borrowing creation decreases book inventory."""
        initial_inventory = book.inventory
        from borrowings.models import Borrowing
        
        Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=14)
        )
        
        book.refresh_from_db()
        assert book.inventory == initial_inventory - 1
    
    def test_borrowing_return_increases_inventory(self, returned_borrowing):
        """Test that borrowing return increases book inventory."""
        book = returned_borrowing.book
        initial_inventory = book.inventory
        
        # Simulate return by setting actual_return_date
        returned_borrowing.actual_return_date = date.today()
        returned_borrowing.save()
        
        book.refresh_from_db()
        assert book.inventory == initial_inventory + 1


@pytest.mark.django_db
class TestBorrowingSerializers:
    """Test borrowing serializers."""
    
    def test_borrowing_list_serializer(self, borrowing):
        """Test BorrowingListSerializer."""
        from borrowings.serializers import BorrowingListSerializer
        
        serializer = BorrowingListSerializer(borrowing)
        data = serializer.data
        
        assert data['id'] == borrowing.id
        assert data['user'] == borrowing.user.id
        assert data['book'] == borrowing.book.id
        assert data['borrow_date'] == borrowing.borrow_date.isoformat()
        assert data['expected_return_date'] == borrowing.expected_return_date.isoformat()
        assert 'is_active' in data
        assert 'is_overdue' in data
    
    def test_borrowing_detail_serializer(self, borrowing):
        """Test BorrowingDetailSerializer."""
        from borrowings.serializers import BorrowingDetailSerializer
        
        serializer = BorrowingDetailSerializer(borrowing)
        data = serializer.data
        
        assert data['id'] == borrowing.id
        assert data['user'] == borrowing.user.id
        assert data['book'] == borrowing.book.id
        assert data['borrow_date'] == borrowing.borrow_date.isoformat()
        assert data['expected_return_date'] == borrowing.expected_return_date.isoformat()
        assert data['actual_return_date'] is None
        assert 'is_active' in data
        assert 'is_overdue' in data
        assert 'overdue_days' in data
    
    def test_borrowing_create_serializer_valid_data(self, book):
        """Test BorrowingCreateSerializer with valid data."""
        from borrowings.serializers import BorrowingCreateSerializer
        
        data = {
            'book': book.id,
            'expected_return_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        serializer = BorrowingCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_borrowing_create_serializer_invalid_data(self, book):
        """Test BorrowingCreateSerializer with invalid data."""
        from borrowings.serializers import BorrowingCreateSerializer
        
        data = {
            'book': book.id,
            'expected_return_date': (date.today() - timedelta(days=1)).isoformat()
        }
        
        serializer = BorrowingCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'expected_return_date' in serializer.errors
    
    def test_borrowing_return_serializer_valid_data(self, borrowing):
        """Test BorrowingReturnSerializer with valid data."""
        from borrowings.serializers import BorrowingReturnSerializer
        
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        serializer = BorrowingReturnSerializer(borrowing, data=data)
        assert serializer.is_valid()
    
    def test_borrowing_return_serializer_invalid_data(self, returned_borrowing):
        """Test BorrowingReturnSerializer with invalid data."""
        from borrowings.serializers import BorrowingReturnSerializer
        
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        serializer = BorrowingReturnSerializer(returned_borrowing, data=data)
        assert not serializer.is_valid()
        assert 'actual_return_date' in serializer.errors


@pytest.mark.django_db
class TestBorrowingPermissions:
    """Test borrowing permissions."""
    
    def test_borrowing_list_permission_authenticated(self, auth_client):
        """Test that borrowing list requires authentication."""
        url = reverse('borrowings:borrowing-list')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_borrowing_detail_permission_authenticated(self, auth_client, borrowing):
        """Test that borrowing detail requires authentication."""
        url = reverse('borrowings:borrowing-detail', kwargs={'pk': borrowing.pk})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_borrowing_create_permission_authenticated(self, auth_client, book):
        """Test that borrowing creation requires authentication."""
        url = reverse('borrowings:borrowing-list')
        data = {
            'book': book.id,
            'expected_return_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_borrowing_return_permission_authenticated(self, auth_client, borrowing):
        """Test that borrowing return requires authentication."""
        url = reverse('borrowings:borrowing-return', kwargs={'pk': borrowing.pk})
        data = {
            'actual_return_date': date.today().isoformat()
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK