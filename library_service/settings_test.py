"""
Test settings for DRF Library project.
"""

from .settings import *
from datetime import timedelta

# Use in-memory database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable debug mode for testing
DEBUG = False

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use console cache backend for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable Django-Q for testing
Q_CLUSTER = {
    'name': 'test_cluster',
    'workers': 1,
    'timeout': 10,
    'retry': 10,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Test-specific middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Test-specific REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Test-specific JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'test-secret-key',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Authorize',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(minutes=10),
}

# Test-specific Stripe settings
STRIPE_PUBLISHABLE_KEY = 'pk_test_test_key'
STRIPE_SECRET_KEY = 'sk_test_test_key'
SITE_URL = 'http://testserver'

# Test-specific Telegram settings
TELEGRAM_BOT_TOKEN = 'test_bot_token'
TELEGRAM_CHAT_ID = 'test_chat_id'

# Test-specific fine settings
FINE_MULTIPLIER = 2.0

# Disable static files collection for tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Test-specific CORS settings
CORS_ALLOWED_ORIGINS = ['http://testserver']

# Disable Spectacular for tests
SPECTACULAR_SETTINGS = {
    'TITLE': 'DRF Library API',
    'DESCRIPTION': 'Library management system API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}