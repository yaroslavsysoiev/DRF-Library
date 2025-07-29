# 📚 DRF Library Management System

Сучасна система управління бібліотекою, побудована на Django REST Framework з інтеграцією Stripe для платежів та Telegram для сповіщень.

## 🚀 Особливості

### Core Functionality
- **👥 User Management**: Реєстрація, аутентифікація та управління профілями
- **📖 Book Management**: CRUD операції для книг з відстеженням інвентаря
- **📚 Borrowing System**: Система позичання та повернення книг
- **💳 Payment Processing**: Інтеграція зі Stripe для платежів та штрафів
- **📱 Notifications**: Telegram інтеграція для сповіщень у реальному часі
- **📊 Analytics**: Комплексна звітність та аналітика
- **⏰ Scheduled Tasks**: Автоматизована обробка штрафів та сповіщень

### Technical Features
- **🔐 JWT Authentication**: Безпечна аутентифікація
- **🛡️ Permissions**: Розширена система дозволів
- **🔍 Filtering & Search**: Просунутий пошук та фільтрація
- **📄 Pagination**: Пагінація для великих наборів даних
- **🐳 Docker Support**: Повна підтримка Docker
- **📈 Monitoring**: Health checks та моніторинг
- **🧪 Testing**: Комплексна система тестування

## 🛠️ Технології

### Backend
- **Django 4.2.7**: Основний фреймворк
- **Django REST Framework 3.14.0**: API фреймворк
- **PostgreSQL**: Основна база даних
- **Redis**: Кешування та черги завдань
- **Django-Q**: Планові завдання

### External Integrations
- **Stripe**: Платежі та штрафи
- **Telegram Bot API**: Сповіщення
- **JWT**: Аутентифікація

### Development & Testing
- **Pytest**: Тестування
- **Factory Boy**: Тестові дані
- **Coverage**: Покриття тестами
- **Docker**: Контейнеризація
- **Nginx**: Reverse proxy

## 📋 Вимоги

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (опціонально)

## 🚀 Швидкий старт

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd DRF-Library
```

### 2. Налаштування середовища
```bash
# Створіть віртуальне середовище
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows

# Встановіть залежності
pip install -r requirements.txt
```

### 3. Налаштування змінних середовища
```bash
# Скопіюйте .env.sample
cp .env.sample .env

# Відредагуйте .env файл
nano .env
```

### 4. База даних
```bash
# Міграції
python manage.py migrate

# Створення суперкористувача
python manage.py createsuperuser
```

### 5. Запуск сервера
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
- **Description**: Інтерактивна документація API

### ReDoc
- **URL**: `http://localhost:8000/api/redoc/`
- **Description**: Альтернативна документація API

## 🔐 Аутентифікація

API використовує JWT (JSON Web Tokens) для аутентифікації.

### Отримання токену
```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Використання токену
```bash
curl -X GET http://localhost:8000/api/books/ \
  -H "Authorization: Authorize <your_token>"
```

## 📊 Основні Endpoints

### Users
- `POST /api/users/register/` - Реєстрація користувача
- `POST /api/users/token/` - Отримання JWT токену
- `POST /api/users/token/refresh/` - Оновлення токену
- `GET /api/users/profile/` - Профіль користувача

### Books
- `GET /api/books/` - Список книг
- `GET /api/books/{id}/` - Деталі книги
- `POST /api/books/` - Створення книги (admin)
- `PUT /api/books/{id}/` - Оновлення книги (admin)
- `DELETE /api/books/{id}/` - Видалення книги (admin)

### Borrowings
- `GET /api/borrowings/` - Список позичень
- `POST /api/borrowings/` - Створення позичання
- `GET /api/borrowings/{id}/` - Деталі позичання
- `PATCH /api/borrowings/{id}/return/` - Повернення книги

### Payments
- `GET /api/payments/` - Список платежів
- `POST /api/payments/` - Створення платежу
- `GET /api/payments/{id}/` - Деталі платежу
- `POST /api/payments/{id}/refund/` - Повернення платежу (admin)

### Analytics
- `GET /api/analytics/revenue/` - Аналітика доходів
- `GET /api/analytics/borrowings/` - Аналітика позичень
- `GET /api/analytics/books/` - Аналітика книг
- `GET /api/analytics/users/` - Аналітика користувачів

## 🔧 Management Commands

### Налаштування планових завдань
```bash
python manage.py setup_tasks
```

### Запуск конкретного завдання
```bash
python manage.py run_task daily_summary
```

### Тестування
```bash
# Запуск всіх тестів
python -m pytest

# Запуск з покриттям
python -m pytest --cov=.

# Запуск конкретного тесту
python -m pytest tests/test_users.py::TestUserRegistration::test_user_registration_success
```

## 📈 Моніторинг

### Health Check
```bash
curl http://localhost:8000/health/
```

### Логи
```bash
# Django логи
tail -f logs/django.log

# Docker логи
docker-compose logs -f web
```

## 🔒 Безпека

### Rate Limiting
- API endpoints: 10 requests/second
- Login endpoints: 5 requests/minute

### Permissions
- **Public**: Перегляд книг
- **Authenticated**: Позичання книг, управління профілем
- **Admin**: Повний доступ до всіх функцій

### Environment Variables
Обов'язкові змінні середовища:
```bash
SECRET_KEY=your-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FINE_MULTIPLIER=2.0
```

## 🧪 Тестування

### Покриття тестами
- **Unit Tests**: Моделі, серіалізатори, permissions
- **Integration Tests**: API endpoints
- **Coverage Target**: 60%+

### Запуск тестів
```bash
# Всі тести
python -m pytest

# З покриттям
python -m pytest --cov=. --cov-report=html

# Конкретний маркер
python -m pytest -m "api"
```

## 📁 Структура проекту

```
DRF-Library/
├── library_service/          # Основні налаштування Django
├── users/                   # Управління користувачами
├── books/                   # Управління книгами
├── borrowings/              # Система позичань
├── payments/                # Платежі та штрафи
├── notifications/           # Telegram сповіщення
├── analytics/               # Аналітика та звіти
├── tasks/                   # Планові завдання
├── tests/                   # Тести
├── nginx/                   # Nginx конфігурація
├── docker-compose.yml       # Docker композиція
├── Dockerfile              # Docker образ
└── requirements.txt         # Python залежності
```

## 🤝 Contributing

1. Fork репозиторію
2. Створіть feature branch (`git checkout -b feature/amazing-feature`)
3. Commit змін (`git commit -m 'Add amazing feature'`)
4. Push до branch (`git push origin feature/amazing-feature`)
5. Відкрийте Pull Request

## 📝 License

Цей проект ліцензований під MIT License - дивіться файл [LICENSE](LICENSE) для деталей.

## 📞 Support

При виникненні проблем:
1. Перевірте [Issues](https://github.com/your-repo/issues)
2. Створіть нове Issue з детальним описом проблеми
3. Перевірте логи: `docker-compose logs`

## 🎯 Roadmap

### Planned Features
- [ ] Email сповіщення
- [ ] SMS сповіщення
- [ ] Мобільний додаток
- [ ] Machine Learning для рекомендацій
- [ ] Blockchain для децентралізованого управління

### Performance Improvements
- [ ] Redis кешування
- [ ] Database оптимізація
- [ ] CDN для статичних файлів
- [ ] Load balancing

---

**Розроблено з ❤️ використовуючи Django REST Framework**
