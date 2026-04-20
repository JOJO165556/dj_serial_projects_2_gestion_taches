from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.routers import router
from api.views.user_views import RegisterView, MeView, LogoutView
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

urlpatterns = [
    path("tasks/reorder/", reorder_tasks, name="reorder_tasks"),

    # Routes des apps via router
    path("", include(router.urls)),

    # Authentification
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
