# Docker Deployment Guide

Цей документ описує як розгорнути DRF Library проект за допомогою Docker.

## 🐳 Prerequisites

- Docker
- Docker Compose
- Git

## 🚀 Quick Start

### 1. Клонування проекту
```bash
git clone <repository-url>
cd DRF-Library
```

### 2. Налаштування змінних середовища
```bash
# Скопіюйте .env.sample
cp .env.sample .env

# Відредагуйте .env файл з вашими налаштуваннями
nano .env
```

### 3. Запуск в режимі розробки
```bash
# Збудувати та запустити контейнери
docker-compose up --build

# Або в фоновому режимі
docker-compose up -d --build
```

### 4. Створення суперкористувача
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Налаштування планових завдань
```bash
docker-compose exec web python manage.py setup_tasks
```

## 🏭 Production Deployment

### 1. Налаштування production змінних
```bash
# Створіть .env файл для production
cp .env.sample .env
# Відредагуйте змінні для production
```

### 2. Запуск production версії
```bash
# Використовуйте production docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Перевірка статусу
```bash
# Перевірте статус контейнерів
docker-compose -f docker-compose.prod.yml ps

# Перевірте логи
docker-compose -f docker-compose.prod.yml logs -f
```

## 📁 Структура проекту

```
DRF-Library/
├── Dockerfile                 # Docker образ для Django
├── docker-compose.yml         # Development композиція
├── docker-compose.prod.yml    # Production композиція
├── .dockerignore             # Файли для ігнорування в Docker
├── nginx/
│   └── nginx.conf           # Nginx конфігурація
├── library_service/
│   ├── settings.py          # Development налаштування
│   └── settings_production.py # Production налаштування
└── requirements.txt          # Python залежності
```

## 🔧 Services

### Web (Django)
- **Port**: 8000
- **Command**: Gunicorn з 4 workers
- **Environment**: Production налаштування

### Worker (Django-Q)
- **Command**: `python manage.py qcluster`
- **Purpose**: Обробка планових завдань

### Database (PostgreSQL)
- **Port**: 5432
- **Volume**: `postgres_data`
- **Purpose**: Основна база даних

### Redis
- **Port**: 6379
- **Volume**: `redis_data`
- **Purpose**: Кеш та черги завдань

### Nginx
- **Port**: 80, 443
- **Purpose**: Reverse proxy та статичні файли

## 🌐 Доступні endpoints

- **API Documentation**: http://localhost/api/docs/
- **ReDoc**: http://localhost/api/redoc/
- **Admin Panel**: http://localhost/admin/
- **Health Check**: http://localhost/health/

## 🔍 Monitoring

### Перевірка здоров'я системи
```bash
curl http://localhost/health/
```

### Перегляд логів
```bash
# Всі сервіси
docker-compose logs

# Конкретний сервіс
docker-compose logs web
docker-compose logs worker
docker-compose logs nginx
```

### Перевірка баз даних
```bash
# PostgreSQL
docker-compose exec db psql -U library_user -d library_db

# Redis
docker-compose exec redis redis-cli
```

## 🛠️ Management Commands

### Django команди
```bash
# Міграції
docker-compose exec web python manage.py migrate

# Створення суперкористувача
docker-compose exec web python manage.py createsuperuser

# Збірка статичних файлів
docker-compose exec web python manage.py collectstatic

# Налаштування завдань
docker-compose exec web python manage.py setup_tasks

# Запуск конкретного завдання
docker-compose exec web python manage.py run_task daily_summary
```

### Docker команди
```bash
# Перезапуск сервісів
docker-compose restart

# Оновлення образів
docker-compose pull

# Очищення невикористаних ресурсів
docker system prune
```

## 🔒 Security

### Environment Variables
- `SECRET_KEY`: Ключ безпеки Django
- `POSTGRES_PASSWORD`: Пароль бази даних
- `STRIPE_SECRET_KEY`: Секретний ключ Stripe
- `TELEGRAM_BOT_TOKEN`: Токен Telegram бота

### Network Security
- Всі сервіси ізольовані в `library_network`
- Nginx налаштований з rate limiting
- Security headers включені

## 📊 Performance

### Оптимізації
- Gunicorn з 4 workers
- Nginx з gzip компресією
- Redis для кешування
- PostgreSQL оптимізований для production

### Моніторинг
- Health check endpoint
- Structured logging
- Error tracking

## 🚨 Troubleshooting

### Проблеми з базою даних
```bash
# Перевірка підключення
docker-compose exec web python manage.py dbshell

# Скидання бази даних
docker-compose down -v
docker-compose up -d
```

### Проблеми з Redis
```bash
# Перевірка Redis
docker-compose exec redis redis-cli ping

# Очищення кешу
docker-compose exec redis redis-cli flushall
```

### Проблеми з Nginx
```bash
# Перевірка конфігурації
docker-compose exec nginx nginx -t

# Перезапуск Nginx
docker-compose restart nginx
```

## 📝 Deployment Checklist

- [ ] Налаштовані всі environment variables
- [ ] База даних мігрується успішно
- [ ] Статичні файли зібрані
- [ ] Суперкористувач створений
- [ ] Планові завдання налаштовані
- [ ] Health check проходить
- [ ] Логи перевірені
- [ ] SSL сертифікати налаштовані (production)
- [ ] Backup стратегія налаштована

## 🔄 Backup & Recovery

### Backup бази даних
```bash
docker-compose exec db pg_dump -U library_user library_db > backup.sql
```

### Restore бази даних
```bash
docker-compose exec -T db psql -U library_user library_db < backup.sql
```

### Backup volumes
```bash
docker run --rm -v library_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 📞 Support

При виникненні проблем:
1. Перевірте логи: `docker-compose logs`
2. Перевірте health endpoint: `curl http://localhost/health/`
3. Перевірте статус контейнерів: `docker-compose ps`