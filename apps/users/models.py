from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES_CHOICES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )
    
    role = models.CharField(max_length=10, choices=ROLES_CHOICES, default="member")