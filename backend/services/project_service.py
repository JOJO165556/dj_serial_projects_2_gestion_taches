"""
Service de gestion des projets.

Contient la logique métier liée aux projets : création (avec initialisation
automatique des colonnes Kanban), ajout de membres et désactivation.
Ce service est utilisé par ProjectViewSet et doit rester découplé de la couche HTTP.
"""

from django.db.models import Q
from apps.users.models import Friendship
from apps.project.models import Project, ProjectInvitation
from services.column_service import create_default_columns
from services.notification_service import send_project_invitation_email


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

def invite_member(project, user=None, email=None, invited_by=None, custom_message=""):
    """Crée une invitation pour un utilisateur (existant ou non) et la retourne."""
    if user:
        # Vérifier si l'utilisateur est déjà membre
        if user in project.members.all() or user == project.owner:
            raise ValueError("L'utilisateur fait déjà partie du projet.")
        
        # Créer ou mettre à jour l'invitation
        invitation, created = ProjectInvitation.objects.update_or_create(
            project=project,
            user=user,
            defaults={'status': 'pending', 'message': custom_message, 'email': user.email}
        )
    elif email:
        # Créer ou mettre à jour l'invitation par email (utilisateur externe)
        invitation, created = ProjectInvitation.objects.update_or_create(
            project=project,
            email=email,
            defaults={'status': 'pending', 'message': custom_message}
        )
    else:
        raise ValueError("Veuillez fournir un utilisateur ou un e-mail.")
    
    if not created:
        invitation.status = 'pending'
        invitation.message = custom_message
        if user:
            invitation.email = user.email
        invitation.save()

    # Vérifier si l'utilisateur est un ami (pour sauter l'email si besoin)
    is_friend = False
    if invited_by and user:
        is_friend = Friendship.objects.filter(
            (Q(sender=invited_by, receiver=user) | Q(sender=user, receiver=invited_by)),
            status="accepted"
        ).exists()

    # Envoi de l'email d'invitation seulement si pas ami (ou si utilisateur externe)
    email_sent = False
    if invited_by and not is_friend:
        # Pour l'email, on utilise l'email de l'invitation
        email_sent = send_project_invitation_email(invitation, invited_by, custom_message)

    invitation._email_sent = email_sent
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
