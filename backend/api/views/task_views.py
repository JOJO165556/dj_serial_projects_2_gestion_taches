from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.task.models import Task
from api.serializers.task_serializer import TaskSerializer
from api.permissions import IsTaskAllowed
from services.task_service import create_task, assign_task, move_task
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
        create_task(
            project=serializer.validated_data["project"],
            column=serializer.validated_data.get("column"),
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            priority=serializer.validated_data.get("priority", "medium"),
        )

    def perform_update(self, serializer):
        task = self.get_object()

        column = serializer.validated_data.get("column")
        assigned_to = serializer.validated_data.get("assigned_to")

        if column:
            move_task(task, column)


        if assigned_to:
            assign_task(task, assigned_to)

        serializer.save()

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
    if tasks.count() != len(tasks_data):
        return Response(
            {"error": "Certaines tâches n'existent pas."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Vérifier les permissions pour chaque tâche
    permission = IsTaskAllowed()
    for task in tasks:
        if not permission.has_object_permission(request, None, task):
            return Response(
                {"error": f"Permission refusée pour la tâche {task.id}"}, 
                status=status.HTTP_403_FORBIDDEN
            )

    with transaction.atomic():
        for task_data in tasks_data:
            Task.objects.filter(id=task_data['id']).update(
                position=task_data['position']
            )

    return Response({"message": "Tasks reordered"})
