from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.users.models import Friendship
from api.serializers.friend_serializer import FriendshipSerializer

@extend_schema(tags=["Relations"])
class FriendshipViewSet(viewsets.ModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Friendship.objects.none()
        
        # Retourne toutes les relations impliquant l'utilisateur (envoyées ou reçues)
        return Friendship.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-created_at')

    @extend_schema(summary="Accepter une demande d'ami")
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response({"detail": "Vous ne pouvez accepter que les demandes qui vous sont adressées."}, status=status.HTTP_403_FORBIDDEN)
        
        if friendship.status != "pending":
            return Response({"detail": "Cette demande n'est plus en attente."}, status=status.HTTP_400_BAD_REQUEST)

        friendship.status = "accepted"
        friendship.save()
        return Response({"status": "Demande d'ami acceptée."})

    @extend_schema(summary="Décliner ou annuler une demande d'ami")
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        friendship = self.get_object()
        if friendship.receiver != request.user and friendship.sender != request.user:
            return Response({"detail": "Action non autorisée."}, status=status.HTTP_403_FORBIDDEN)

        if friendship.status != "pending":
            return Response({"detail": "Cette demande n'est plus en attente."}, status=status.HTTP_400_BAD_REQUEST)

        friendship.status = "declined"
        friendship.save()
        return Response({"status": "Demande d'ami refusée."})
