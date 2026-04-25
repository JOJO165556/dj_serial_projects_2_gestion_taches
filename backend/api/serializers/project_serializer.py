from rest_framework import serializers
from django.utils import timezone
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
        write_only=True,
        required=False
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
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "start_date": {"required": False},
            "end_date": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        owner = attrs.get("owner") or getattr(self.instance, "owner", None)
        members = attrs.get("members")
        attrs.setdefault("start_date", getattr(self.instance, "start_date", timezone.now()))
        if members is not None and owner and owner not in members:
            attrs["members"] = list(members) + [owner]
        return attrs
