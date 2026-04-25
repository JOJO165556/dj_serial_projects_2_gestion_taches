"""
Service de gestion des projets.

Contient la logique métier liée aux projets : création (avec initialisation
automatique des colonnes Kanban), ajout de membres et désactivation.
Ce service est utilisé par ProjectViewSet et doit rester découplé de la couche HTTP.
"""

from apps.project.models import Project, ProjectInvitation
from services.column_service import create_default_columns


def create_project(name, description, owner, start_date):
    """Crée un projet et initialise ses colonnes Kanban par défaut."""
    project = Project.objects.create(
        name=name,
        description=description,
        owner=owner,
        start_date=start_date,
    )
    project.members.add(owner)
    create_default_columns(project)
    return project

def invite_member(project, user):
    """Crée une invitation pour un utilisateur et la retourne."""
    # Vérifier si l'utilisateur est déjà membre
    if user in project.members.all() or user == project.owner:
        raise ValueError("L'utilisateur fait déjà partie du projet.")
    
    # Vérifier s'il y a déjà une invitation en attente
    invitation, created = ProjectInvitation.objects.get_or_create(
        project=project,
        user=user,
        defaults={'status': 'pending'}
    )
    
    if not created and invitation.status in ['accepted', 'declined']:
        invitation.status = 'pending'
        invitation.save()
        
    return invitation

def respond_invitation(invitation, action):
    """Accepte ou décline une invitation."""
    if action == 'accept':
        invitation.status = 'accepted'
        invitation.project.members.add(invitation.user)
        if invitation.user.role == "reader":
            invitation.user.role = "member"
            invitation.user.save(update_fields=["role"])
    elif action == 'decline':
        invitation.status = 'declined'
    else:
        raise ValueError("Action invalide.")
    
    invitation.save()
    return invitation
def deactivate_project(project):
    # Désactiver projet
    project.is_active = False
    project.save()
    return project
