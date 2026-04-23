from apps.users.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(username, password, email, role="member"):
    # Créer utilisateur
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role
    )
       
    return user 

def update_user(user, data):
    # Mettre à jour utilisateur
    if "username" in data:
        user.username = data["username"]
        
    if "email" in data:
        user.email = data["email"]
        
    if "password" in data and data["password"]:
        user.set_password(data["password"])
        
    user.save()
    return user