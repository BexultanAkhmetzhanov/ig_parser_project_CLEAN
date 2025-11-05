import os
from dotenv import load_dotenv

import dj_database_url
from pathlib import Path

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

# --- Твои ALLOWED_HOSTS (все правильно) ---
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] # Для локальной разработки

FLY_HOSTNAME = "ig-parser-project.fly.dev"
if FLY_HOSTNAME:
    ALLOWED_HOSTS.append(FLY_HOSTNAME)

NETLIFY_HOSTNAME = "promo-finder.netlify.app"
if NETLIFY_HOSTNAME:
    ALLOWED_HOSTS.append(NETLIFY_HOSTNAME)

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
# --- КОНЕЦ ALLOWED_HOSTS ---


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    

    # Наши приложения
    'locations.apps.LocationsConfig',
    'categories.apps.CategoriesConfig',
    'establishments.apps.EstablishmentsConfig',
    'promotions.apps.PromotionsConfig',
]

# --- Твой MIDDLEWARE (все правильно) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# --- КОНЕЦ MIDDLEWARE ---

ROOT_URLCONF = 'ig_parser_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ig_parser_project.wsgi.application'

# Database (все правильно)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# --- Твой CORS (все правильно) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://promo-finder.netlify.app",
]
# --- КОНЕЦ CORS ---

MEDIA_URL = '/media/'

# Путь в файловой системе, где будут храниться загруженные файлы
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки Django REST Framework (все правильно)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}