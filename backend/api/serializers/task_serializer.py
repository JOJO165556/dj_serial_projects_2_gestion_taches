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

    def validate(self, attrs):
        request = self.context.get("request")
        project = attrs.get("project") or getattr(self.instance, "project", None)
        column = attrs.get("column", getattr(self.instance, "column", None))
        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))

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

        if column and project and column.project_id != project.id:
            raise serializers.ValidationError(
                {"column": "La colonne doit appartenir au projet de la tâche."}
            )

        if assigned_to and project:
            is_member = assigned_to == project.owner or project.members.filter(id=assigned_to.id).exists()
            if not is_member:
                raise serializers.ValidationError(
                    {"assigned_to": "L'utilisateur assigné doit appartenir au projet."}
                )

        return attrs

class TaskReorderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()
    column_id = serializers.IntegerField(required=False, allow_null=True)

class TaskReorderSerializer(serializers.Serializer):
    tasks = TaskReorderItemSerializer(many=True)
