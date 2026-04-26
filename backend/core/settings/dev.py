from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5173', # Port par défaut pour Vue.js/Vite
    ]

INSTALLED_APPS += [
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True