"""
Tests for Users app.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_user_registration_success(self, api_client):
        """Test successful user registration."""
        url = reverse('users:register')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == 'test@example.com'
        assert response.data['user']['first_name'] == 'Test'
        assert response.data['user']['last_name'] == 'User'
    
    def test_user_registration_password_mismatch(self, api_client):
        """Test user registration with password mismatch."""
        url = reverse('users:register')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_user_registration_invalid_email(self, api_client):
        """Test user registration with invalid email."""
        url = reverse('users:register')
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_user_registration_duplicate_email(self, api_client, user):
        """Test user registration with duplicate email."""
        url = reverse('users:register')
        data = {
            'email': user.email,
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestJWTToken:
    """Test JWT token functionality."""
    
    def test_jwt_token_obtain_success(self, api_client, user):
        """Test successful JWT token obtain."""
        url = reverse('users:token_obtain_pair')
        data = {
            'email': user.email,
            'password': user.password
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_jwt_token_obtain_invalid_credentials(self, api_client):
        """Test JWT token obtain with invalid credentials."""
        url = reverse('users:token_obtain_pair')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_jwt_token_refresh_success(self, api_client, user):
        """Test successful JWT token refresh."""
        refresh = RefreshToken.for_user(user)
        url = reverse('users:token_refresh')
        data = {
            'refresh': str(refresh)
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_jwt_token_refresh_invalid_token(self, api_client):
        """Test JWT token refresh with invalid token."""
        url = reverse('users:token_refresh')
        data = {
            'refresh': 'invalid_token'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile functionality."""
    
    def test_user_profile_retrieve_success(self, auth_client, user):
        """Test successful user profile retrieval."""
        url = reverse('users:profile')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name
    
    def test_user_profile_retrieve_unauthorized(self, api_client):
        """Test user profile retrieval without authentication."""
        url = reverse('users:profile')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_profile_update_success(self, auth_client, user):
        """Test successful user profile update."""
        url = reverse('users:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
    
    def test_user_profile_update_invalid_data(self, auth_client):
        """Test user profile update with invalid data."""
        url = reverse('users:profile')
        data = {
            'email': 'invalid-email'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test user creation."""
        from users.models import User
        
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_superuser_creation(self):
        """Test superuser creation."""
        from users.models import User
        
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        assert admin.email == 'admin@example.com'
        assert admin.is_staff is True
        assert admin.is_superuser is True
    
    def test_user_str_representation(self, user):
        """Test user string representation."""
        assert str(user) == user.email
    
    def test_user_get_full_name(self, user):
        """Test user get_full_name method."""
        expected_name = f"{user.first_name} {user.last_name}"
        assert user.get_full_name() == expected_name
    
    def test_user_get_short_name(self, user):
        """Test user get_short_name method."""
        assert user.get_short_name() == user.first_name


@pytest.mark.django_db
class TestUserSerializers:
    """Test user serializers."""
    
    def test_user_create_serializer_valid_data(self):
        """Test UserCreateSerializer with valid data."""
        from users.serializers import UserCreateSerializer
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_user_create_serializer_password_mismatch(self):
        """Test UserCreateSerializer with password mismatch."""
        from users.serializers import UserCreateSerializer
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors
    
    def test_user_detail_serializer(self, user):
        """Test UserDetailSerializer."""
        from users.serializers import UserDetailSerializer
        
        serializer = UserDetailSerializer(user)
        data = serializer.data
        
        assert data['email'] == user.email
        assert data['first_name'] == user.first_name
        assert data['last_name'] == user.last_name
        assert 'password' not in data
    
    def test_user_update_serializer(self, user):
        """Test UserUpdateSerializer."""
        from users.serializers import UserUpdateSerializer
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        serializer = UserUpdateSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_user = serializer.save()
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'Name'