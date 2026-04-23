from django.db import models
from apps.project.models import Project
from apps.users.models import User


class Column(models.Model):
    """Colonne d'un Kanban, appartient à un projet"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="columns"
    )
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#6366f1", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="unique_column_name_per_project"
            )
        ]

    def __str__(self):
        return f"{self.project.name} — {self.name}"


class Task(models.Model):
    """Modèle Tâche rattachée à une colonne du Kanban"""
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    column = models.ForeignKey(
        Column,
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True,
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

class TaskAuditLog(models.Model):
    # Historique des modifications d'une tache
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.task.title} - {self.field_name} changed"