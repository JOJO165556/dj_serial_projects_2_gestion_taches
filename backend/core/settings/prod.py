import os

from .base import *

DEBUG = False
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://dj-serial-projects-2-gestion-taches-dwkxtht8j.vercel.app",
    "https://dj-serial-projects-2-gestion-taches-49pfwdqxv.vercel.app",
    "https://dj-serial-projects-2-gestion-taches-glyyj1rzq.vercel.app",
    "https://dj-serial-projects-2-gestion-taches.vercel.app",
]
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "access-control-allow-origin",
]
CSRF_TRUSTED_ORIGINS = [
    "https://dj-serial-projects-2-gestion-taches-dwkxtht8j.vercel.app",
    "https://dj-serial-projects-2-gestion-taches-49pfwdqxv.vercel.app",
    "https://dj-serial-projects-2-gestion-taches-glyyj1rzq.vercel.app",
] + [origin.strip().rstrip('/') for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

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

