"""
Django settings for Sportradar_Backend_v2 project.
Refactored for clarity and robustness with Cloudinary integration.
"""
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# --- 1. Définitions de base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. Gestion de l'environnement et des secrets ---
IS_PRODUCTION = 'RENDER' in os.environ
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-une-cle-locale-par-defaut-NON-SECURISEE')
DEBUG = not IS_PRODUCTION

# --- 3. Configuration des hôtes (ALLOWED_HOSTS) ---
ALLOWED_HOSTS = []
if IS_PRODUCTION:
    RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    ALLOWED_HOSTS = ['*']

# --- 4. Applications installées ---
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'corsheaders',
    'users.apps.UsersConfig',
    'companies.apps.CompaniesConfig',
    'activities.apps.ActivitiesConfig',
    'bookings.apps.BookingsConfig',
    'weather.apps.WeatherConfig',
]

# --- 5. Middleware ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 6. URLs et Templates ---
ROOT_URLCONF = 'Sportradar_Backend_v2.urls'
WSGI_APPLICATION = 'Sportradar_Backend_v2.wsgi.application'
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
# --- 7. Base de données ---
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

db_url = os.getenv('DATABASE_URL')
print("db_url=========",db_url)

if db_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=db_url,
            conn_max_age=600,
            ssl_require=True  # TRÈS IMPORTANT pour Render depuis l'extérieur
        )
    }
    print("🚀 Tentative de connexion à la base externe de Render...")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- 8. Validation des mots de passe ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- 9. Internationalisation (i18n) ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- 10. Fichiers statiques et médias ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'

# Compatibilité packages tiers
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Configuration du stockage pour Django 4.2+
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}

# --- 11. Modèle d'utilisateur personnalisé ---
AUTH_USER_MODEL = 'users.CustomUser'

# --- 12. Configuration des frameworks (DRF, JWT, etc.) ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(days=1), "REFRESH_TOKEN_LIFETIME": timedelta(days=7)}
SPECTACULAR_SETTINGS = {'TITLE': 'SportRadar API', 'DESCRIPTION': 'API pour le projet SportRadar', 'VERSION': '1.0.0', 'SERVE_INCLUDE_SCHEMA': False}
JAZZMIN_SETTINGS = {'site_title': 'SportRadar Admin', 'welcome_sign': 'Bienvenue dans SportRadar', 'show_sidebar': True, 'navigation_expanded': True}

# --- 13. CORS et CSRF ---
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173","http://localhost:5175", "https://sportradar-front.onrender.com"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173","http://localhost:5175", "https://sportradar-front.onrender.com"]

# --- 14. Configuration de Cloudinary ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME' ),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# --- 15. Clés d'API externes ---
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
