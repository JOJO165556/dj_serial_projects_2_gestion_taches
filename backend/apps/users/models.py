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