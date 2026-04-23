"""
Serializer pour les tâches.

TaskSerializer valide et sérialise les données d'une tâche.
Le champ `column` (FK vers Column) remplace l'ancien champ `status` fixe,
rendant le Kanban dynamique et personnalisable par projet.
"""

from rest_framework import serializers
from apps.task.models import Task, Column
from apps.project.models import Project
from apps.users.models import User


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    column = serializers.PrimaryKeyRelatedField(
        queryset=Column.objects.all(),
        allow_null=True,
        required=False,
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "column",
            "position",
            "assigned_to",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

class TaskReorderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()
    column_id = serializers.IntegerField(required=False, allow_null=True)

class TaskReorderSerializer(serializers.Serializer):
    tasks = TaskReorderItemSerializer(many=True)