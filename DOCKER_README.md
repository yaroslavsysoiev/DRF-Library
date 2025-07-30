# Docker Deployment Guide

This document describes how to deploy the DRF Library project using Docker.

## 🐳 Prerequisites

- Docker
- Docker Compose
- Git

## 🚀 Quick Start

### 1. Clone the project
```bash
git clone <repository-url>
cd DRF-Library
```

### 2. Environment variables setup
```bash
# Copy .env.sample
cp .env.sample .env

# Edit .env file with your settings
nano .env
```

### 3. Run in development mode
```bash
# Build and run containers
docker-compose up --build

# Or in background mode
docker-compose up -d --build
```

### 4. Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Setup scheduled tasks
```bash
docker-compose exec web python manage.py setup_tasks
```

## 🏭 Production Deployment

### 1. Production environment variables setup
```bash
# Create .env file for production
cp .env.sample .env
# Edit variables for production
```

### 2. Run production version
```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Check status
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📁 Project Structure

```
DRF-Library/
├── Dockerfile                 # Docker image for Django
├── docker-compose.yml         # Development composition
├── docker-compose.prod.yml    # Production composition
├── .dockerignore             # Files to ignore in Docker
├── nginx/
│   └── nginx.conf           # Nginx configuration
├── library_service/
│   ├── settings.py          # Development settings
│   └── settings_production.py # Production settings
└── requirements.txt          # Python dependencies
```

## 🔧 Services

### Web (Django)
- **Port**: 8000
- **Command**: Gunicorn with 4 workers
- **Environment**: Production settings

### Worker (Django-Q)
- **Command**: `python manage.py qcluster`
- **Purpose**: Processing scheduled tasks

### Database (PostgreSQL)
- **Port**: 5432
- **Volume**: `postgres_data`
- **Purpose**: Main database

### Redis
- **Port**: 6379
- **Volume**: `redis_data`
- **Purpose**: Cache and task queues

### Nginx
- **Port**: 80, 443
- **Purpose**: Reverse proxy and static files

## 🌐 Available endpoints

- **API Documentation**: http://localhost/api/docs/
- **ReDoc**: http://localhost/api/redoc/
- **Admin Panel**: http://localhost/admin/
- **Health Check**: http://localhost/health/

## 🔍 Monitoring

### System health check
```bash
curl http://localhost/health/
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs worker
docker-compose logs nginx
```

### Database check
```bash
# PostgreSQL
docker-compose exec db psql -U library_user -d library_db

# Redis
docker-compose exec redis redis-cli
```

## 🛠️ Management Commands

### Django commands
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Setup tasks
docker-compose exec web python manage.py setup_tasks

# Run specific task
docker-compose exec web python manage.py run_task daily_summary
```

### Docker commands
```bash
# Restart services
docker-compose restart

# Update images
docker-compose pull

# Clean unused resources
docker system prune
```

## 🔒 Security

### Environment Variables
- `SECRET_KEY`: Django security key
- `POSTGRES_PASSWORD`: Database password
- `STRIPE_SECRET_KEY`: Stripe secret key
- `TELEGRAM_BOT_TOKEN`: Telegram bot token

### Network Security
- All services isolated in `library_network`
- Nginx configured with rate limiting
- Security headers enabled

## 📊 Performance

### Optimizations
- Gunicorn with 4 workers
- Nginx with gzip compression
- Redis for caching
- PostgreSQL optimized for production

### Monitoring
- Health check endpoint
- Structured logging
- Error tracking

## 🚨 Troubleshooting

### Database issues
```bash
# Check connection
docker-compose exec web python manage.py dbshell

# Reset database
docker-compose down -v
docker-compose up -d
```

### Redis issues
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli flushall
```

### Nginx issues
```bash
# Check configuration
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

## 📝 Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrations successful
- [ ] Static files collected
- [ ] Superuser created
- [ ] Scheduled tasks configured
- [ ] Health check passes
- [ ] Logs checked
- [ ] SSL certificates configured (production)
- [ ] Backup strategy configured

## 🔄 Backup & Recovery

### Database backup
```bash
docker-compose exec db pg_dump -U library_user library_db > backup.sql
```

### Database restore
```bash
docker-compose exec -T db psql -U library_user library_db < backup.sql
```

### Volume backup
```bash
docker run --rm -v library_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Check health endpoint: `curl http://localhost/health/`
3. Check container status: `docker-compose ps`