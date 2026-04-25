"""
Service de gestion des tâches.

Contient la logique métier liée aux tâches : création dans une colonne,
assignation à un utilisateur, et déplacement entre les colonnes du Kanban.
Ce service est utilisé par TaskViewSet et doit rester découplé de la couche HTTP.
"""

from apps.task.models import Task, Column


def create_task(project, column=None, title="", description="", priority="medium"):
    """
    Crée une tâche dans une colonne donnée d'un projet.

    Si aucune colonne n'est précisée, la tâche est automatiquement placée
    dans la première colonne du projet (order=0, généralement 'To Do').
    """
    if column is None:
        column = Column.objects.filter(project=project).order_by('order').first()

    last_task = (
        Task.objects.filter(project=project, column=column)
        .order_by("-position")
        .first()
    )
    next_position = (last_task.position + 1) if last_task else 0

    return Task.objects.create(
        project=project,
        column=column,
        title=title,
        description=description,
        priority=priority,
        position=next_position,
    )


def assign_task(task, user):
    """Assigne une tâche à un utilisateur."""
    if user and user != task.project.owner and user not in task.project.members.all():
        raise ValueError("L'utilisateur assigné doit appartenir au projet.")
    task.assigned_to = user
    task.save()
    return task


def move_task(task, column):
    """Déplace une tâche vers une autre colonne du Kanban."""
    if task.column == column:
        return task
    if column and column.project_id != task.project_id:
        raise ValueError("La colonne cible n'appartient pas au projet de la tâche.")

    task.column = column
    task.save()
    return task
