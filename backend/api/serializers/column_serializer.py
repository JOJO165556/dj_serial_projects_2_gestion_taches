"""
Serializer pour les colonnes Kanban.

ColumnSerializer expose les colonnes d'un projet avec leurs tâches imbriquées
en lecture seule. Cela permet au frontend Vue.js de charger tout le board
Kanban en un seul appel GET /api/columns/?project=<id>.
"""

from rest_framework import serializers
from apps.task.models import Column
from api.serializers.task_serializer import TaskSerializer


class ColumnSerializer(serializers.ModelSerializer):
    """Serializer pour les colonnes Kanban, avec les tâches imbriquées en lecture."""

    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = [
            "id",
            "project",
            "name",
            "order",
            "color",
            "created_at",
            "tasks",
        ]
        read_only_fields = ["created_at"]
