from rest_framework.viewsets import ModelViewSet
from apps.task.models import Task
from api.serializers.task_serializer import TaskSerializer
from api.permissions import IsTaskAllowed
from services.task_service import create_task, assign_task, move_task
from drf_spectacular.utils import extend_schema, extend_schema_view


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
