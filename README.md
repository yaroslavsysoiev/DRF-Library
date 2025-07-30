# 📚 DRF Library Management System

A modern library management system built on Django REST Framework with Stripe integration for payments and Telegram for notifications.

## 🚀 Features

### Core Functionality
- **👥 User Management**: Registration, authentication, and profile management
- **📖 Book Management**: CRUD operations for books with inventory tracking
- **📚 Borrowing System**: Book borrowing and return system
- **💳 Payment Processing**: Stripe integration for payments and fines
- **📱 Notifications**: Telegram integration for real-time notifications
- **📊 Analytics**: Comprehensive reporting and analytics
- **⏰ Scheduled Tasks**: Automated fine processing and notifications

### Technical Features
- **🔐 JWT Authentication**: Secure authentication
- **🛡️ Permissions**: Advanced permission system
- **🔍 Filtering & Search**: Advanced search and filtering
- **📄 Pagination**: Pagination for large datasets
- **🐳 Docker Support**: Full Docker support
- **📈 Monitoring**: Health checks and monitoring
- **🧪 Testing**: Comprehensive testing system

## 🛠️ Technologies

### Backend
- **Django 4.2.7**: Main framework
- **Django REST Framework 3.14.0**: API framework
- **PostgreSQL**: Main database
- **Redis**: Caching and task queues
- **Django-Q**: Scheduled tasks

### External Integrations
- **Stripe**: Payments and fines
- **Telegram Bot API**: Notifications
- **JWT**: Authentication

### Development & Testing
- **Pytest**: Testing
- **Factory Boy**: Test data
- **Coverage**: Test coverage
- **Docker**: Containerization
- **Nginx**: Reverse proxy

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd DRF-Library
```

### 2. Environment setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment variables setup
```bash
# Copy .env.sample
cp .env.sample .env

# Edit .env file
nano .env
```

### 4. Database
```bash
# Migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Start server
```bash
python manage.py runserver
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📚 API Documentation

### Swagger UI
- **URL**: `http://localhost:8000/api/docs/`
- **Description**: Interactive API documentation

### ReDoc
- **URL**: `http://localhost:8000/api/redoc/`
- **Description**: Alternative API documentation

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Getting a token
```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Using the token
```bash
curl -X GET http://localhost:8000/api/books/ \
  -H "Authorization: Authorize <your_token>"
```

## 📊 Main Endpoints

### Users
- `POST /api/users/register/` - User registration
- `POST /api/users/token/` - Get JWT token
- `POST /api/users/token/refresh/` - Refresh token
- `GET /api/users/profile/` - User profile

### Books
- `GET /api/books/` - List books
- `GET /api/books/{id}/` - Book details
- `POST /api/books/` - Create book (admin)
- `PUT /api/books/{id}/` - Update book (admin)
- `DELETE /api/books/{id}/` - Delete book (admin)

### Borrowings
- `GET /api/borrowings/` - List borrowings
- `POST /api/borrowings/` - Create borrowing
- `GET /api/borrowings/{id}/` - Borrowing details
- `PATCH /api/borrowings/{id}/return/` - Return book

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/{id}/` - Payment details
- `POST /api/payments/{id}/refund/` - Refund payment (admin)

### Analytics
- `GET /api/analytics/revenue/` - Revenue analytics
- `GET /api/analytics/borrowings/` - Borrowing analytics
- `GET /api/analytics/books/` - Book analytics
- `GET /api/analytics/users/` - User analytics

## 🔧 Management Commands

### Setup scheduled tasks
```bash
python manage.py setup_tasks
```

### Run specific task
```bash
python manage.py run_task daily_summary
```

### Testing
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test
python -m pytest tests/test_users.py::TestUserRegistration::test_user_registration_success
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health/
```

### Logs
```bash
# Django logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f web
```

## 🔒 Security

### Rate Limiting
- API endpoints: 10 requests/second
- Login endpoints: 5 requests/minute

### Permissions
- **Public**: View books
- **Authenticated**: Borrow books, manage profile
- **Admin**: Full access to all features

### Environment Variables
Required environment variables:
```bash
SECRET_KEY=your-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FINE_MULTIPLIER=2.0
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Models, serializers, permissions
- **Integration Tests**: API endpoints
- **Coverage Target**: 60%+

### Running Tests
```bash
# All tests
python -m pytest

# With coverage
python -m pytest --cov=. --cov-report=html

# Specific marker
python -m pytest -m "api"
```

## 📁 Project Structure

```
DRF-Library/
├── library_service/          # Main Django settings
├── users/                   # User management
├── books/                   # Book management
├── borrowings/              # Borrowing system
├── payments/                # Payments and fines
├── notifications/           # Telegram notifications
├── analytics/               # Analytics and reports
├── tasks/                   # Scheduled tasks
├── tests/                   # Tests
├── nginx/                   # Nginx configuration
├── docker-compose.yml       # Docker composition
├── Dockerfile              # Docker image
└── requirements.txt         # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter issues:
1. Check [Issues](https://github.com/your-repo/issues)
2. Create new Issue with detailed problem description
3. Check logs: `docker-compose logs`

## 🎯 Roadmap

### Planned Features
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Mobile application
- [ ] Machine Learning for recommendations
- [ ] Blockchain for decentralized management

### Performance Improvements
- [ ] Redis caching
- [ ] Database optimization
- [ ] CDN for static files
- [ ] Load balancing

---

**Developed with ❤️ using Django REST Framework**
