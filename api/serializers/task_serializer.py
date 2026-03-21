from rest_framework import serializers
from apps.task.models import Task
from apps.project.models import Project
from apps.users.models import User

class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True, 
        required=False
    )
    
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "assigned_to",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
            ]