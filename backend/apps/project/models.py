from django.db import models
from apps.users.models import User
import uuid

class Project(models.Model):
    # Modèle Projet
    name = models.CharField(max_length=60)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    members = models.ManyToManyField(User, related_name="projects")
    start_date =models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)

class ProjectInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_invitations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.status})"