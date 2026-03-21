from apps.users.models import User

def create_user(username, password, role="member"):
    user = User.objects.create_user(
        username=username,
        password=password,
        role=role
    )
    
    return user 