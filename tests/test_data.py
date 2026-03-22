import os
import django
from django.utils import timezone
from datetime import timedelta

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User
from services.user_service import create_user
from services.project_service import create_project, add_member
from services.task_service import create_task

def populate():
    print("Création d'utilisateurs de test...")
    user1, _ = User.objects.get_or_create(username="AliceTest", email="alice@test.com")
    if _: user1.set_password("password123"); user1.save()
    
    user2, _ = User.objects.get_or_create(username="BobTest", email="bob@test.com")
    if _: user2.set_password("password123"); user2.save()
    
    print("Création de projets...")
    p1 = create_project(
        name="Refonte du site web",
        description="Améliorer le design avec un CSS minimaliste.",
        owner=user1,
        start_date=timezone.now()
    )
    add_member(p1, user2)

    p2 = create_project(
    project1.members.add(user2)

    project2 = create_project(
        name="Application Mobile",
        description="Développer l'application React Native.",
        owner=user2,
        start_date=timezone.now()
    )

    print("Ajout des utilisateurs de test aux projets de test...")
    for user in (user1, user2):
        project1.members.add(user)
        project2.members.add(user)

    print("Création de tâches...")
    t1 = create_task(project=project1, title="Créer base.html", description="Mettre en place le template principal.", priority="high")
    t2 = create_task(project=project1, title="Ajouter du style", description="Ajouter styles.css avec des ombres légères.", priority="medium")
    t3 = create_task(project=project2, title="Initialiser le projet", description="npx react-native init App", priority="high")
    
    # Assignation manuelle car le service n'affecte pas l'utilisateur lors de la création
    t1.assigned_to = user1
    t1.save()
    t2.assigned_to = user2
    t2.save()
    t3.assigned_to = user2
    t3.save()

    print("Données de test ajoutées avec succès !")

if __name__ == '__main__':
    populate()
