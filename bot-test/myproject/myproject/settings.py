import os
from pathlib import Path
from decouple import config, Csv

# Inicjalizacja Config
# Ścieżka do katalogu głównego projektu
BASE_DIR = Path(__file__).resolve().parent.parent

# Sekretne klucze
SECRET_KEY = config('DJANGO_SECRET_KEY', default='fallback_secret')
SECRET_KEY_JIRA = config('SECRET_KEY', default='fallback_jira_secret')

# Tryb debugowania
DEBUG = config('DEBUG', default=False, cast=bool)

# Lista dozwolonych hostów

# Aplikacje Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'myapp',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Konfiguracja URL
ROOT_URLCONF = 'myproject.urls'

# Szablony
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplikacja WSGI
WSGI_APPLICATION = 'myproject.wsgi.application'

# Baza danych
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='boty-db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
    }
}

# Walidacja haseł
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Konfiguracja języka i czasu
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'CET'
USE_I18N = True
USE_TZ = True

# Pliki statyczne
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'myapp/static'] if DEBUG else []
STATIC_ROOT = BASE_DIR / 'staticfiles'
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Pliki media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Tworzenie katalogu na logi, jeśli nie istnieje
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Logowanie
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/scheduler.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'scheduler': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Klucz domyślny dla modeli
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ustawienia logowania i wylogowania
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
