import os

from .base import *

DEBUG = False
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [origin.strip().rstrip('/') for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]
CSRF_TRUSTED_ORIGINS = [origin.strip().rstrip('/') for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
# On s'assure que les domaines Vercel sont aussi dans CSRF_TRUSTED_ORIGINS si besoin
# mais CSRF ne supporte pas nativement les regex, donc il faut les lister manuellement dans l'env var.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CORS_ALLOW_CREDENTIALS = True

# Cookies cross-origin (Vercel → Render)
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

# JWT refresh token cookie cross-origin
SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] = "None"
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True

