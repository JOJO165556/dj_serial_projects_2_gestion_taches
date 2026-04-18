from django.contrib import admin
from django.urls import path, include
from api.routers import router
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("", include("apps.users.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
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
