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

    def validate(self, attrs):
        request = self.context.get("request")
        project = attrs.get("project") or getattr(self.instance, "project", None)

        if request and project:
            user = request.user
            is_member = project.owner_id == user.id or project.members.filter(id=user.id).exists()
            can_edit = user.role in ["admin", "member"] or project.owner_id == user.id

            if not is_member:
                raise serializers.ValidationError(
                    {"project": "Vous n'avez pas acces a ce projet."}
                )
            if request.method not in ("GET", "HEAD", "OPTIONS") and not can_edit:
                raise serializers.ValidationError(
                    {"project": "Votre role ne permet pas de modifier ce projet."}
                )

        return attrs
