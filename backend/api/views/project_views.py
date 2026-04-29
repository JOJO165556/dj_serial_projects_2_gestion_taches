from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Case, When, Value, IntegerField, Q
from apps.project.models import Project
from apps.users.models import User
from apps.task.models import Task, Column
from api.serializers.project_serializer import ProjectSerializer
from api.serializers.task_serializer import TaskSerializer
from api.permissions import IsProjectAllowed
from services.project_service import create_project, invite_member, respond_invitation, deactivate_project
from services.kanban_service import get_full_kanban_board
from apps.project.models import ProjectInvitation
from rest_framework.views import APIView
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        summary="Lister les projets",
        description="Retourne tous les projets accessibles à l'utilisateur.",
        tags=["Projets"],
    ),
    create=extend_schema(
        summary="Créer un projet",
        description=(
            "Crée un nouveau projet. Trois colonnes Kanban par défaut "
            "(To Do, In Progress, Done) sont automatiquement créées."
        ),
        tags=["Projets"],
    ),
    retrieve=extend_schema(summary="Détail d'un projet", tags=["Projets"]),
    update=extend_schema(summary="Mettre à jour un projet", tags=["Projets"]),
    partial_update=extend_schema(summary="Mise à jour partielle d'un projet", tags=["Projets"]),
    destroy=extend_schema(summary="Supprimer un projet", tags=["Projets"]),
)
class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectAllowed]

    def get_queryset(self):
        # Ne retourner que les projets dont l'utilisateur est owner ou membre
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        project = create_project(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            owner=self.request.user,
            start_date=serializer.validated_data.get("start_date")
        )
        serializer.instance = project

    @extend_schema(
        summary="Lister les invitations reçues",
        description="Retourne toutes les invitations de projet en attente pour l'utilisateur connecté.",
        tags=["Projets"],
    )
    @action(detail=False, methods=["get"])
    def received_invitations(self, request):
        invitations = ProjectInvitation.objects.filter(
            user=request.user,
            status="pending"
        ).select_related("project", "project__owner")
        
        data = [{
            "token": str(inv.token),
            "project_name": inv.project.name,
            "owner_username": inv.project.owner.username,
            "created_at": inv.created_at,
            "message": inv.message
        } for inv in invitations]
        
        return Response(data)

    @extend_schema(
        summary="Ajouter un membre au projet",
        description="Crée une invitation pour un utilisateur via son `user_id` ou son `email` et retourne le token d'invitation.",
        tags=["Projets"],
    )
    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()

        user_id = request.data.get("user_id")
        email = request.data.get("email")
        message = request.data.get("message", "")
        user = None
        
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email=email).first()
        else:
            return Response({"error": "Veuillez fournir un user_id ou un email."}, status=400)

        try:
            invitation = invite_member(
                project, 
                user=user, 
                email=email if not user else None,
                invited_by=request.user,
                custom_message=message
            )
            return Response({
                "message": f"Invitation envoyée à {user.email if user else email}",
                "token": str(invitation.token),
                "email_sent": getattr(invitation, '_email_sent', False),
                "email_error": getattr(invitation, '_email_error', None)
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    def perform_update(self, serializer):
        serializer.save()

    @extend_schema(
        summary="Vue Kanban d'un projet",
        description="Retourne le board Kanban structuré avec colonnes et tâches filtrées.",
        tags=["Projets"],
        parameters=[
            OpenApiParameter(name="priority", description="Filtrer par priorité (low, medium, high)", required=False, type=str),
            OpenApiParameter(name="deadline", description="Filtrer par date limite (YYYY-MM-DD)", required=False, type=str),
            OpenApiParameter(name="overdue", description="Si 'true', retourne les tâches en retard (exclut celles de la colonne Done)", required=False, type=str),
            OpenApiParameter(name="search", description="Filtrer par titre de tâche", required=False, type=str),
        ]
    )
    @action(detail=True, methods=["get"])
    def kanban(self, request, pk=None):
        project = self.get_object()
        cache_key = f'kanban_board_{project.id}'
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
            
        response_data = get_full_kanban_board(project)
        
        # Mettre en cache (ex: 15 minutes)
        cache.set(cache_key, response_data, timeout=900)

        return Response(response_data)

class ProjectInvitationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Détails de l'invitation",
        description="Récupère les informations d'une invitation via son token.",
        tags=["Projets"],
    )
    def get(self, request, token):
        try:
            invitation = ProjectInvitation.objects.get(token=token)
        except ProjectInvitation.DoesNotExist:
            return Response({"error": "Invitation introuvable"}, status=404)

        # Expiration : 7 jours après création
        expires_at = invitation.created_at + timedelta(days=7)
        if timezone.now() > expires_at:
            return Response({"error": "Ce lien d'invitation a expiré (validité : 7 jours)."}, status=410)

        # On renvoie les infos de base sans vérifier l'utilisateur 
        return Response({
            "token": str(invitation.token),
            "status": invitation.status,
            "expires_at": expires_at.isoformat(),
            "project": {
                "id": invitation.project.id,
                "name": invitation.project.name,
                "description": invitation.project.description or "",
                "members_count": invitation.project.members.count() + 1, # +1 pour le proprio
                "columns": [
                    {"id": c.id, "name": c.name, "color": c.color} 
                    for c in invitation.project.columns.all().order_by('order')
                ]
            },
            "owner": {
                "id": invitation.project.owner.id,
                "username": invitation.project.owner.username,
                "email": invitation.project.owner.email,
            },
            "user_email": invitation.user.email if invitation.user else invitation.email, # Email attendu pour cette invitation
            "is_logged_in": request.user.is_authenticated,
            "is_correct_user": request.user == invitation.user if request.user.is_authenticated else False
        })

    @extend_schema(
        summary="Répondre à une invitation",
        description="Accepte ou décline une invitation (action: 'accept' ou 'decline').",
        tags=["Projets"],
    )
    def post(self, request, token):
        if not request.user.is_authenticated:
            return Response({"error": "Vous devez être connecté pour répondre à une invitation."}, status=401)

        try:
            invitation = ProjectInvitation.objects.get(token=token)
        except ProjectInvitation.DoesNotExist:
            return Response({"error": "Invitation introuvable"}, status=404)
            
        if invitation.user:
            if invitation.user != request.user:
                return Response(
                    {"error": f"Cette invitation est destinée à {invitation.user.email}, mais vous êtes connecté avec le compte {request.user.email}."}, 
                    status=403
                )
        else:
            # Invitation par e-mail pur : on vérifie que l'e-mail correspond
            if invitation.email != request.user.email:
                return Response(
                    {"error": f"Cette invitation est destinée à {invitation.email}, mais vous êtes connecté avec le compte {request.user.email}."}, 
                    status=403
                )
            # On lie l'invitation à l'utilisateur maintenant
            invitation.user = request.user
            invitation.save()
            
        # Expiration : 7 jours après création
        expires_at = invitation.created_at + timedelta(days=7)
        if timezone.now() > expires_at:
            return Response({"error": "Ce lien d'invitation a expiré (validité : 7 jours)."}, status=410)

        action = request.data.get("action")
        try:
            respond_invitation(invitation, action)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
            
        return Response({"message": f"Invitation {action}ed"})