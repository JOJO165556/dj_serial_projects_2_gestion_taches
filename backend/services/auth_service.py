from urllib.parse import urlencode

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from services.notification_service import send_magic_link_email


MAGIC_LINK_SALT = "gestion_taches.magic_link"


def _get_signer():
    return TimestampSigner(salt=MAGIC_LINK_SALT)


def create_magic_link_token(user):
    signer = _get_signer()
    return signer.sign(str(user.pk))


def build_magic_link_url(user):
    token = create_magic_link_token(user)
    query = urlencode({"token": token, "email": user.email})
    return f"{settings.FRONTEND_URL}/auth/magic?{query}"


def request_magic_link(email):
    user = User.objects.filter(email__iexact=email, is_active=True).order_by("id").first()
    if not user:
        return None

    magic_url = build_magic_link_url(user)
    send_magic_link_email(user, magic_url)
    return user


def verify_magic_link(email, token):
    signer = _get_signer()
    try:
        unsigned_value = signer.unsign(
            token,
            max_age=settings.MAGIC_LINK_MAX_AGE_SECONDS,
        )
    except SignatureExpired as exc:
        raise ValueError("Ce lien de connexion a expire.") from exc
    except BadSignature as exc:
        raise ValueError("Ce lien de connexion est invalide.") from exc

    user = User.objects.filter(
        id=unsigned_value,
        email__iexact=email,
        is_active=True,
    ).first()
    if not user:
        raise ValueError("Aucun utilisateur valide ne correspond a ce lien.")

    refresh = RefreshToken.for_user(user)
    return {
        "user": user,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
