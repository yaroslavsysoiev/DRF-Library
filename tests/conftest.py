"""
Pytest configuration and fixtures for DRF Library tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from factory import Faker
from factory.django import DjangoModelFactory
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
    
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = Faker('password')
    is_active = True


class AdminUserFactory(DjangoModelFactory):
    """Factory for creating admin users."""
    
    class Meta:
        model = User
    
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = Faker('password')
    is_active = True
    is_staff = True
    is_superuser = True


class BookFactory(DjangoModelFactory):
    """Factory for creating test books."""
    
    class Meta:
        model = Book
    
    title = Faker('sentence', nb_words=3)
    author = Faker('name')
    cover = Faker('random_element', elements=['HARD', 'SOFT'])
    inventory = Faker('random_int', min=1, max=10)
    daily_fee = Faker('pydecimal', left_digits=2, right_digits=2, positive=True)


class BorrowingFactory(DjangoModelFactory):
    """Factory for creating test borrowings."""
    
    class Meta:
        model = Borrowing
    
    user = None  # Will be set in tests
    book = None  # Will be set in tests
    borrow_date = Faker('date_this_year')
    expected_return_date = Faker('future_date', end_date='+30d')


class PaymentFactory(DjangoModelFactory):
    """Factory for creating test payments."""
    
    class Meta:
        model = Payment
    
    borrowing = None  # Will be set in tests
    status = Faker('random_element', elements=['PENDING', 'PAID', 'EXPIRED'])
    type = Faker('random_element', elements=['PAYMENT', 'FINE'])
    money_to_pay = Faker('pydecimal', left_digits=3, right_digits=2, positive=True)


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Create and return a test user."""
    return UserFactory()


@pytest.fixture
def admin_user():
    """Create and return a test admin user."""
    return AdminUserFactory()


@pytest.fixture
def book():
    """Create and return a test book."""
    return BookFactory()


@pytest.fixture
def borrowing(user, book):
    """Create and return a test borrowing."""
    return BorrowingFactory(user=user, book=book)


@pytest.fixture
def payment(borrowing):
    """Create and return a test payment."""
    return PaymentFactory(borrowing=borrowing)


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Authorize {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated admin API client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Authorize {refresh.access_token}')
    return api_client


@pytest.fixture
def multiple_books():
    """Create and return multiple test books."""
    return [BookFactory() for _ in range(5)]


@pytest.fixture
def multiple_users():
    """Create and return multiple test users."""
    return [UserFactory() for _ in range(3)]


@pytest.fixture
def multiple_borrowings(multiple_users, multiple_books):
    """Create and return multiple test borrowings."""
    borrowings = []
    for i, user in enumerate(multiple_users):
        book = multiple_books[i % len(multiple_books)]
        borrowings.append(BorrowingFactory(user=user, book=book))
    return borrowings


@pytest.fixture
def overdue_borrowing(user, book):
    """Create and return an overdue borrowing."""
    from datetime import date, timedelta
    overdue_date = date.today() - timedelta(days=5)
    return BorrowingFactory(
        user=user,
        book=book,
        borrow_date=overdue_date - timedelta(days=10),
        expected_return_date=overdue_date,
        actual_return_date=None
    )


@pytest.fixture
def returned_borrowing(user, book):
    """Create and return a returned borrowing."""
    from datetime import date, timedelta
    borrow_date = date.today() - timedelta(days=10)
    expected_return = date.today() - timedelta(days=5)
    actual_return = date.today() - timedelta(days=3)
    return BorrowingFactory(
        user=user,
        book=book,
        borrow_date=borrow_date,
        expected_return_date=expected_return,
        actual_return_date=actual_return
    )


@pytest.fixture
def paid_payment(borrowing):
    """Create and return a paid payment."""
    return PaymentFactory(
        borrowing=borrowing,
        status='PAID',
        type='PAYMENT'
    )


@pytest.fixture
def fine_payment(overdue_borrowing):
    """Create and return a fine payment."""
    return PaymentFactory(
        borrowing=overdue_borrowing,
        status='PENDING',
        type='FINE'
    )


@pytest.fixture
def mock_stripe_service(mocker):
    """Mock Stripe service for testing."""
    mock_service = mocker.patch('payments.services.StripeService')
    mock_service.return_value.create_payment_session.return_value = {
        'session_id': 'test_session_id',
        'session_url': 'http://test.com/session',
        'amount': 1000
    }
    mock_service.return_value.verify_payment_session.return_value = True
    mock_service.return_value.create_refund.return_value = {
        'id': 'test_refund_id',
        'status': 'succeeded'
    }
    return mock_service


@pytest.fixture
def mock_telegram_service(mocker):
    """Mock Telegram service for testing."""
    mock_service = mocker.patch('notifications.services.TelegramNotificationService')
    mock_service.return_value.send_message.return_value = True
    mock_service.return_value.send_borrowing_notification.return_value = True
    mock_service.return_value.send_return_notification.return_value = True
    mock_service.return_value.send_payment_notification.return_value = True
    mock_service.return_value.send_overdue_notification.return_value = True
    mock_service.return_value.send_daily_summary.return_value = True
    return mock_service


@pytest.fixture
def mock_analytics_service(mocker):
    """Mock Analytics service for testing."""
    mock_service = mocker.patch('analytics.services.AnalyticsService')
    mock_service.return_value.get_revenue_analytics.return_value = {
        'total_revenue': 1000.00,
        'total_payments': 10,
        'avg_daily_revenue': 100.00
    }
    mock_service.return_value.get_borrowing_analytics.return_value = {
        'total_borrowings': 20,
        'returned_books': 15,
        'return_rate': 75.0
    }
    mock_service.return_value.get_book_analytics.return_value = {
        'popular_books': [],
        'avg_daily_fee': 5.00,
        'total_inventory': 100
    }
    return mock_service