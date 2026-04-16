from django.urls import path
from .views import task_list, task_detail, task_create, task_edit

urlpatterns = [
    path("", task_list, name="task_list"),
    path("create/", task_create, name="task_create"),
    path("<int:pk>/", task_detail, name="task_detail"),
    path("<int:pk>/edit/", task_edit, name="task_edit"),
]
