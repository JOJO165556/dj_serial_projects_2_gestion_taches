from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.task.models import Task, TaskAuditLog
from api.serializers.task_serializer import TaskSerializer
from api.permissions import IsTaskAllowed
from services.task_service import create_task, assign_task, move_task
from services.kanban_service import get_full_kanban_board
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.serializers.task_serializer import TaskSerializer, TaskReorderSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Lister toutes les tâches",
        description="Retourne la liste de toutes les tâches accessibles à l'utilisateur.",
        tags=["Tâches"],
    ),
    create=extend_schema(
        summary="Créer une tâche",
        description=(
            "Crée une nouvelle tâche dans une colonne d'un projet. "
            "Le champ `column` doit être l'ID d'une colonne appartenant au projet."
        ),
        tags=["Tâches"],
    ),
    retrieve=extend_schema(
        summary="Détail d'une tâche",
        tags=["Tâches"],
    ),
    update=extend_schema(
        summary="Mettre à jour une tâche",
        description=(
            "Met à jour les données d'une tâche. "
            "Pour déplacer une tâche dans le Kanban, modifiez le champ `column`."
        ),
        tags=["Tâches"],
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'une tâche (ex: déplacer dans le Kanban)",
        tags=["Tâches"],
    ),
    destroy=extend_schema(
        summary="Supprimer une tâche",
        tags=["Tâches"],
    ),
)
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.select_related("project", "column", "assigned_to")
    serializer_class = TaskSerializer
    permission_classes = [IsTaskAllowed]

    def perform_create(self, serializer):
        task = create_task(
            project=serializer.validated_data["project"],
            column=serializer.validated_data.get("column"),
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            priority=serializer.validated_data.get("priority", "medium"),
        )
        _broadcast_board_update(task.project)

    def perform_update(self, serializer):
        task = self.get_object()

        # On garde l'ancienne valeur pour comparer
        old_column = task.column
        old_assigned = task.assigned_to
        
        column = serializer.validated_data.get("column")
        assigned_to = serializer.validated_data.get("assigned_to")

        if column and column != old_column:
            move_task(task, column)
            TaskAuditLog.objects.create(
                task=task,
                user=self.request.user,
                field_name="column",
                old_value=str(old_column.name) if old_column else "",
                new_value=str(column.name)
            )

        if assigned_to and assigned_to != old_assigned:
            assign_task(task, assigned_to)
            TaskAuditLog.objects.create(
                task=task,
                user=self.request.user,
                field_name="assigned_to",
                old_value=str(old_assigned.username) if old_assigned else "",
                new_value=str(assigned_to.username)
            )

        serializer.save()
        _broadcast_board_update(task.project)
        
    def perform_destroy(self, instance):
        project = instance.project
        instance.delete()
        _broadcast_board_update(project)
        
def _broadcast_board_update(project):
    # Invalider le cache
    cache_key = f'kanban_board_{project.id}'
    cache.delete(cache_key)
    
    # Recuperer le nouveau board complet
    new_board = get_full_kanban_board(project)
    
    # Mettre en cache
    cache.set(cache_key, new_board, timeout=900)
    
    # Notifier via Channels avec le payload complet
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'kanban_updates_{project.id}',
        {
            'type': 'kanban_update',
            'message': 'board_updated',
            'board_data': new_board
        }
    )

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reorder_tasks(request):
    serializer = TaskReorderSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tasks_data = serializer.validated_data['tasks']
    task_ids = [t['id'] for t in tasks_data]
    
    # Vérifier que toutes les tâches existent
    tasks = Task.objects.filter(id__in=task_ids)
    task_map = {task.id: task for task in tasks}
    
    if len(task_map) != len(tasks_data):
        return Response(
            {"error": "Certaines tâches n'existent pas."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Vérifier les permissions pour chaque tâche et préparer la mise à jour
    permission = IsTaskAllowed()
    tasks_to_update = []
    
    for task_data in tasks_data:
        task = task_map[task_data['id']]
        if not permission.has_object_permission(request, None, task):
            return Response(
                {"error": f"Permission refusée pour la tâche {task.id}"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.position = task_data['position']
        if 'column_id' in task_data and task_data['column_id'] is not None:
            task.column_id = task_data['column_id']
        
        tasks_to_update.append(task)

    try:
        with transaction.atomic():
            Task.objects.bulk_update(tasks_to_update, ['position', 'column_id'])
            
            if tasks_to_update:
                _broadcast_board_update(tasks_to_update[0].project)
            
    except Exception as e:
        # En cas d'erreur BD, transaction.atomic() fera un rollback automatiquement
        return Response(
            {"error": f"Erreur lors de la mise à jour : {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({"message": "Tasks reordered"})
