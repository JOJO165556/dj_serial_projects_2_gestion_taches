from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
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
from rest_framework.permissions import IsAuthenticated
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
        summary="Ajouter un membre au projet",
        description="Crée une invitation pour un utilisateur existant via son `user_id` et retourne le token d'invitation.",
        tags=["Projets"],
    )
    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()

        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)

        try:
            invitation = invite_member(project, user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
            
        return Response({
            "message": "Invitation créée",
            "token": str(invitation.token)
        })

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
    permission_classes = [IsAuthenticated]

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
            
        if invitation.user != request.user:
            return Response({"error": "Non autorisé"}, status=403)
            
        return Response({
            "project_name": invitation.project.name,
            "owner_name": invitation.project.owner.username,
            "status": invitation.status
        })

    @extend_schema(
        summary="Répondre à une invitation",
        description="Accepte ou décline une invitation (action: 'accept' ou 'decline').",
        tags=["Projets"],
    )
    def post(self, request, token):
        try:
            invitation = ProjectInvitation.objects.get(token=token)
        except ProjectInvitation.DoesNotExist:
            return Response({"error": "Invitation introuvable"}, status=404)
            
        if invitation.user != request.user:
            return Response({"error": "Non autorisé"}, status=403)
            
        action = request.data.get("action")
        try:
            respond_invitation(invitation, action)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
            
        return Response({"message": f"Invitation {action}ed"})