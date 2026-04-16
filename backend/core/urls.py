from django.contrib import admin
from django.urls import path, include
from api.routers import router

urlpatterns = [
    path("", include("apps.users.urls")),
    path('admin/', admin.site.urls),
    path('api/', include("api.urls")),
    path("projects/", include("apps.project.urls")),
    path("tasks/", include("apps.task.urls")),
]
