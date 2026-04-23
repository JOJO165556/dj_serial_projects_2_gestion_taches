from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from api.routers import router
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Redirection racine vers Vue.js (dev: 5173, prod: adapter)
    path("", RedirectView.as_view(url="http://localhost:5173/", permanent=False)),

    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    # Routes template Django conservees pour l'historique
    path("users/", include("apps.users.urls")),
    path("projects/", include("apps.project.urls")),
    path("tasks/", include("apps.task.urls")),

    # Documentation OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
