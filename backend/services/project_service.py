"""
Service de gestion des projets.

Contient la logique métier liée aux projets : création (avec initialisation
automatique des colonnes Kanban), ajout de membres et désactivation.
Ce service est utilisé par ProjectViewSet et doit rester découplé de la couche HTTP.
"""

from apps.project.models import Project
from services.column_service import create_default_columns


def create_project(name, description, owner, start_date):
    """Crée un projet et initialise ses colonnes Kanban par défaut."""
    project = Project.objects.create(
        name=name,
        description=description,
        owner=owner,
        start_date=start_date,
    )
    create_default_columns(project)
    return project

def add_member(project, user):
    # Ajouter membre
    project.members.add(user)
    return project

def deactivate_project(project):
    # Désactiver projet
    project.is_active = False
    project.save()
    return project