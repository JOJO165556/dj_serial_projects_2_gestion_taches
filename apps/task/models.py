from django.db import models
from apps.project.models import Project
from apps.users.models import User

class Task(models.Model):
    # Modèle Tâche
    title = models.CharField(max_length=150)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="tasks", null=True, blank=True)
    status = models.CharField(max_length=10, choices=[("todo", "To Do") , ("doing", "Doing"), ("done", "Done")], default="todo")
    priority = models.CharField(max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium")
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)