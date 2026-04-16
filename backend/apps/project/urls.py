from django.urls import path
from .views import project_list, project_detail, project_create, project_edit

urlpatterns = [
    path("", project_list, name="project_list"),
    path("create/", project_create, name="project_create"),
    path("<int:pk>/", project_detail, name="project_detail"),
    path("<int:pk>/edit/", project_edit, name="project_edit"),
]
