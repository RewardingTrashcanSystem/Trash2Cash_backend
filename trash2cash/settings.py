from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl

# ======================
# LOAD ENVIRONMENT VARIABLES
# ======================
load_dotenv()

# ======================
# BASE DIR
# ======================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECURITY
# ======================
SECRET_KEY = os.environ.get('SECRET_KEY', 't3rR3nd3r-!xL$8k#2m@p9v&u7q*1z!d4w^y0h5r3b')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    'trash2cash-backend-hclt.onrender.com',
    'localhost',
    '127.0.0.1',
    'trash2cash-backend-1.onrender.com',
]

# ======================
# APPLICATIONS
# ======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Local apps
    'user',
    'history',
]

AUTH_USER_MODEL = 'user.User'

# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================
# URLS / WSGI
# ======================
ROOT_URLCONF = 'trash2cash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'trash2cash.wsgi.application'

# ======================
# DATABASE - NEON POSTGRESQL
# ======================
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse Neon PostgreSQL connection URL
    try:
        tmpPostgres = urlparse(DATABASE_URL)
        
        # Extract database name (remove leading slash)
        db_name = tmpPostgres.path.replace('/', '')
        if not db_name:
            db_name = 'neondb'  # Default database name
        
        # Extract query parameters
        query_params = dict(parse_qsl(tmpPostgres.query))
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': tmpPostgres.username,
                'PASSWORD': tmpPostgres.password,
                'HOST': tmpPostgres.hostname,
                'PORT': tmpPostgres.port or 5432,
                'OPTIONS': query_params,
            }
        }
        
        # Ensure sslmode is set for Neon
        if 'sslmode' not in DATABASES['default']['OPTIONS']:
            DATABASES['default']['OPTIONS']['sslmode'] = 'require'
        
        print(f"✅ Connected to Neon PostgreSQL: {tmpPostgres.hostname}")
        
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        # Fallback to SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        print("⚠️ Falling back to SQLite database")
else:
    # Fallback to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("⚠️ DATABASE_URL not set. Using SQLite for local development.")

# ======================
# PASSWORD VALIDATION
# ======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======================
# REST FRAMEWORK / JWT
# ======================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ======================
# STATIC FILES
# ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ======================
# MEDIA FILES
# ======================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
os.makedirs(MEDIA_ROOT, exist_ok=True)

# ======================
# CORS
# ======================
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ======================
# DEFAULT PK
# ======================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'