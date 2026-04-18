from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from api.serializers.user_serializer import UserSerializer, RegisterSerializer
from api.permissions import IsUserSelfOrAdmin
from services.user_service import create_user, update_user
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary="Lister les utilisateurs", tags=["Utilisateurs"]),
    create=extend_schema(summary="Créer un utilisateur", tags=["Utilisateurs"]),
    retrieve=extend_schema(summary="Détail d'un utilisateur", tags=["Utilisateurs"]),
    update=extend_schema(summary="Mettre à jour un utilisateur", tags=["Utilisateurs"]),
    partial_update=extend_schema(summary="Mise à jour partielle", tags=["Utilisateurs"]),
    destroy=extend_schema(summary="Supprimer un utilisateur", tags=["Utilisateurs"]),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserSelfOrAdmin]

    def perform_create(self, serializer):
        user = create_user(**serializer.validated_data)
        serializer.instance = user

    def perform_update(self, serializer):
        user = self.get_object()
        user = update_user(user, serializer.validated_data)
        serializer.instance = user


@extend_schema(
    summary="Créer un compte",
    description="Endpoint public pour l'inscription. Aucune authentification requise.",
    tags=["Authentification"],
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    summary="Profil de l'utilisateur connecté",
    description="Retourne les informations de l'utilisateur authentifié via le token JWT.",
    tags=["Authentification"],
)
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    summary="Déconnexion",
    description=(
        "Invalide le `refresh` token côté serveur (blacklist). "
        "Après cette requête, le token ne peut plus être utilisé pour obtenir un nouvel `access` token. "
        "Le client doit supprimer ses tokens du stockage local."
    ),
    tags=["Authentification"],
    request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}, 'required': ['refresh']}},
    responses={204: None},
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response(
                {'detail': 'Token invalide ou déjà révoqué.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
