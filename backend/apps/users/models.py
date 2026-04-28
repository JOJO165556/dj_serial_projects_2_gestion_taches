from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Modèle Utilisateur
    ROLES_CHOICES = (
        ("admin", "Administrateur"),
        ("member", "Membre"),
        ("reader", "Lecteur"),
    )
    
    role = models.CharField(max_length=10, choices=ROLES_CHOICES, default="reader")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

class Friendship(models.Model):
    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("accepted", "Accepté"),
        ("declined", "Refusé"),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sender", "receiver")
        verbose_name = "Ami"
        verbose_name_plural = "Amis"

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"