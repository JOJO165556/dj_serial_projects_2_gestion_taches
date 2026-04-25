import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")
django.setup()

from apps.users.models import User
from services.project_service import create_project
from services.task_service import create_task, assign_task


def populate():
    print("Creation d'utilisateurs de test...")
    user1, created = User.objects.get_or_create(
        username="AliceTest",
        defaults={"email": "alice@test.com", "role": "admin"},
    )
    if created:
        user1.set_password("password123")
        user1.save()

    user2, created = User.objects.get_or_create(
        username="BobTest",
        defaults={"email": "bob@test.com", "role": "member"},
    )
    if created:
        user2.set_password("password123")
        user2.save()

    print("Creation de projets...")
    project1, _ = create_project(
        name="Refonte du site web",
        description="Ameliorer le design avec un CSS minimaliste.",
        owner=user1,
        start_date=timezone.now(),
    ), None
    project1.members.add(user2)

    project2, _ = create_project(
        name="Application Mobile",
        description="Developper l'application React Native.",
        owner=user2,
        start_date=timezone.now(),
    ), None
    project2.members.add(user1)

    print("Creation de taches...")
    t1 = create_task(
        project=project1,
        title="Creer base.html",
        description="Mettre en place le template principal.",
        priority="high",
    )
    t2 = create_task(
        project=project1,
        title="Ajouter du style",
        description="Ajouter styles.css avec des ombres legeres.",
        priority="medium",
    )
    t3 = create_task(
        project=project2,
        title="Initialiser le projet",
        description="Configurer le socle mobile.",
        priority="high",
    )

    assign_task(t1, user1)
    assign_task(t2, user2)
    assign_task(t3, user2)

    print("Donnees de test ajoutees avec succes.")


if __name__ == "__main__":
    populate()
