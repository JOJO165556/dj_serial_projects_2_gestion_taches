from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.routers import router
from api.views.user_views import (
    RegisterView,
    MeView,
    LogoutView,
    MagicLinkRequestView,
    MagicLinkVerifyView,
)
from drf_spectacular.utils import extend_schema

# Override du tag par défaut des vues JWT ("auth" → "Authentification")
TokenObtainPairView = extend_schema(
    summary="Obtenir les tokens JWT (login)",
    description="Retourne un `access` token (60 min) et un `refresh` token (1 jour). Passez le `access` dans le header `Authorization: Bearer <token>` pour toutes les requêtes protégées.",
    tags=["Authentification"],
)(TokenObtainPairView)

TokenRefreshView = extend_schema(
    summary="Rafraîchir le token d'accès",
    description="Échange le `refresh` token contre un nouveau `access` token. L'ancien `refresh` token est invalidé (rotation activée).",
    tags=["Authentification"],
)(TokenRefreshView)

from api.views.task_views import reorder_tasks
from api.views.project_views import ProjectInvitationView

urlpatterns = [
    path("tasks/reorder/", reorder_tasks, name="reorder_tasks"),
    path("projects/invitations/<uuid:token>/", ProjectInvitationView.as_view(), name="project_invitation"),

    # Routes des apps via router
    path("", include(router.urls)),

    # Authentification
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/magic-link/", MagicLinkRequestView.as_view(), name="magic_link_request"),
    path("auth/magic-link/verify/", MagicLinkVerifyView.as_view(), name="magic_link_verify"),
]
