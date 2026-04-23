from rest_framework import serializers
from apps.project.models import Project
from apps.users.models import User
from api.serializers.user_serializer import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    # Lecture : objets complets
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    # Ecriture : IDs uniquement
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="owner",
        write_only=True
    )
    members_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        source="members",
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "owner_id",
            "members",
            "members_ids",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]