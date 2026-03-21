from rest_framework import serializers
from apps.project.models import Project
from apps.users.models import User

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]