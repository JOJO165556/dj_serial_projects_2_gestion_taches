from rest_framework import serializers
from apps.users.models import Friendship, User
from api.serializers.user_serializer import UserSerializer

class FriendshipSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="receiver",
        write_only=True
    )

    class Meta:
        model = Friendship
        fields = ["id", "sender", "receiver", "receiver_id", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "sender", "status", "created_at", "updated_at"]

    def validate_receiver_id(self, value):
        request = self.context.get("request")
        if request and request.user == value:
            raise serializers.ValidationError("Vous ne pouvez pas vous envoyer une demande d'ami à vous-même.")
        return value

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver = validated_data["receiver"]
        
        # Vérifier si une demande existe déjà
        existing_friendship = Friendship.objects.filter(
            sender=sender, receiver=receiver
        ).first() or Friendship.objects.filter(
            sender=receiver, receiver=sender
        ).first()

        if existing_friendship:
            raise serializers.ValidationError("Une demande d'ami ou une amitié existe déjà entre ces deux utilisateurs.")

        return Friendship.objects.create(sender=sender, receiver=receiver, status="pending")
