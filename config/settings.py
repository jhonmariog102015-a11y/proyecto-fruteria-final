import os
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Optimización técnica para pruebas automatizadas:
# Al ejecutar 'manage.py test', se emplea MD5PasswordHasher para acelerar la suite
# de pruebas (evitando los cálculos costosos de PBKDF2 que retrasan la ejecución).
if 'test' in sys.argv:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

# --- 1. GESTIÓN COMPATIBLE DE VARIABLES DE ENTORNO (.env) ---
# Compatible con django-environ o fallback nativo de os.environ para que cualquier persona pueda ejecutar el proyecto
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, True),
        EMAIL_HOST_USER=(str, 'alpasofruteria029@gmail.com'),
        EMAIL_HOST_PASSWORD=(str, ''),
        DEFAULT_FROM_EMAIL=(str, 'Al Paso Frutería <alpasofruteria029@gmail.com>'),
    )
    env_file = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_file):
        environ.Env.read_env(env_file)
except ImportError:
    class EnvFallback:
        def __call__(self, key, default=None):
            return os.environ.get(key, default)

        def bool(self, key, default=True):
            val = os.environ.get(key)
            if val is None:
                return default
            return str(val).lower() in ('1', 'true', 'yes', 'on')
    env = EnvFallback()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-_up6x&lapw^956f!#*n^f9t+8y@#gnb9%dj8y03-658diwbd$4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True) if hasattr(env, 'bool') else bool(env('DEBUG', default=True))

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'principal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'principal' / 'templates',
        ],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Backends de autenticación (soporta inicio de sesión por nombre de usuario o correo electrónico)
AUTHENTICATION_BACKENDS = [
    'principal.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Seguridad de sesiones para empleados y administradores
SESSION_COOKIE_AGE = 86400  # 24 horas de vigencia máxima de sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierre automático de sesión al cerrar el navegador
SESSION_COOKIE_HTTPONLY = True  # Protección contra robo de cookies vía JavaScript (XSS)

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Redirecciones de autenticación
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# --- 2. CONFIGURACIÓN SMTP USANDO VARIABLES DE ENTORNO ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='alpasofruteria029@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Al Paso Frutería <alpasofruteria029@gmail.com>')
SERVER_EMAIL = EMAIL_HOST_USER
