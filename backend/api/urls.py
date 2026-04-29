from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.routers import router
from api.views.user_views import (
    RegisterView,
    MeView,
    LogoutView,
    MagicLinkRequestView,
    MagicLinkVerifyView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    HealthCheckView,
)
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

# Override du tag par défaut des vues JWT ("auth" → "Authentification")
CookieTokenObtainPairView = extend_schema(
    summary="Obtenir les tokens JWT (login)",
    description="Retourne un `access` token (60 min) dans le JSON et un `refresh` token (1 jour) dans un cookie sécurisé. Passez le `access` dans le header `Authorization: Bearer <token>` pour toutes les requêtes protégées.",
    tags=["Authentification"],
    responses={
        200: inline_serializer(
            name='CookieTokenObtainPairResponse',
            fields={
                'access': serializers.CharField(),
            }
        )
    }
)(CookieTokenObtainPairView)

CookieTokenRefreshView = extend_schema(
    summary="Rafraîchir le token d'accès",
    description="Lit le `refresh` token depuis le cookie et retourne un nouveau `access` token. Le cookie refresh est mis à jour.",
    tags=["Authentification"],
    responses={
        200: inline_serializer(
            name='CookieTokenRefreshResponse',
            fields={
                'access': serializers.CharField(),
            }
        )
    }
)(CookieTokenRefreshView)

from api.views.task_views import reorder_tasks
from api.views.project_views import ProjectInvitationView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("tasks/reorder/", reorder_tasks, name="reorder_tasks"),
    path("projects/invitations/<uuid:token>/", ProjectInvitationView.as_view(), name="project_invitation"),

    # Routes des apps via router
    path("", include(router.urls)),

    # Authentification
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/magic-link/", MagicLinkRequestView.as_view(), name="magic_link_request"),
    path("auth/magic-link/verify/", MagicLinkVerifyView.as_view(), name="magic_link_verify"),
]
