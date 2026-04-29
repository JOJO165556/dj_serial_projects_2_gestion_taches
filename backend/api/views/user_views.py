from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from api.serializers.user_serializer import (
    UserSerializer,
    RegisterSerializer,
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
)
from api.permissions import IsUserSelfOrAdmin
from services.user_service import create_user, update_user
from services.auth_service import request_magic_link, verify_magic_link
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.conf import settings

User = get_user_model()


@extend_schema_view(
    create=extend_schema(summary="Créer un utilisateur", tags=["Utilisateurs"]),
    retrieve=extend_schema(summary="Détail d'un utilisateur", tags=["Utilisateurs"]),
    update=extend_schema(summary="Mettre à jour un utilisateur", tags=["Utilisateurs"]),
    partial_update=extend_schema(summary="Mise à jour partielle", tags=["Utilisateurs"]),
    destroy=extend_schema(summary="Supprimer un utilisateur", tags=["Utilisateurs"]),
    list=extend_schema(
        summary="Liste des utilisateurs / Recherche",
        description="Par défaut, ne retourne que l'utilisateur connecté. Utilisez `search` pour chercher d'autres utilisateurs par leur username.",
        parameters=[
            OpenApiParameter(name="search", description="Rechercher par @username (partiel)", required=False, type=str),
        ],
        tags=["Utilisateurs"]
    ),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserSelfOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()
        
        queryset = User.objects.filter(is_active=True).order_by("username")
        
        # Filtre de recherche par nom d'utilisateur (@username)
        search_username = self.request.query_params.get("search", None)
        if search_username:
            # Recherche d'amis par username
            return queryset.filter(username__icontains=search_username).exclude(id=user.id)
            
        # Par défaut, on ne retourne que soi-même pour protéger la vie privée
        return queryset.filter(id=user.id)

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
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201:
            # Création automatique des tokens pour connexion immédiate
            user = User.objects.get(username=response.data['username'])
            refresh = RefreshToken.for_user(user)
            
            response.data['access'] = str(refresh.access_token)
            response.data['user'] = UserSerializer(user).data
            
            # Attacher le cookie de refresh
            _set_refresh_cookie(response, str(refresh))
            
        return response


@extend_schema(
    summary="Demander un magic link",
    description="Envoie un lien de connexion par email si un compte actif correspond a l'adresse fournie.",
    tags=["Authentification"],
)
class MagicLinkRequestView(APIView):
    serializer_class = MagicLinkRequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = MagicLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_magic_link(serializer.validated_data["email"])
        return Response(
            {
                "message": "Si un compte existe pour cet email, un lien de connexion a ete envoye."
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Verifier un magic link",
    description="Valide un lien de connexion et retourne les tokens JWT si le lien est valide.",
    tags=["Authentification"],
)
class MagicLinkVerifyView(APIView):
    serializer_class = MagicLinkVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MagicLinkVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            auth_data = verify_magic_link(
                email=serializer.validated_data["email"],
                token=serializer.validated_data["token"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response = Response(
            {
                "access": auth_data["access"],
                "user": UserSerializer(auth_data["user"]).data,
            },
            status=status.HTTP_200_OK,
        )
        _set_refresh_cookie(response, auth_data["refresh"])
        return response


@extend_schema(
    summary="Profil de l'utilisateur connecté",
    description="Retourne les informations de l'utilisateur authentifié via le token JWT.",
    tags=["Authentification"],
)
class MeView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    summary="Déconnexion",
    description=(
        "Invalide le `refresh` token côté serveur (blacklist). "
        "Après cette requête, le token ne peut plus être utilisé pour obtenir un nouvel `access` token. "
        "Supprime également le cookie du refresh token."
    ),
    tags=["Authentification"],
    responses={204: None},
)
class LogoutView(APIView):
    serializer_class = serializers.Serializer # Serializer vide pour Swagger
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        refresh_token = request.COOKIES.get(cookie_name)
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass # Already blacklisted or invalid
        
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(cookie_name)
        return response


def _set_refresh_cookie(response, refresh_token_value):
    """Attache le cookie de refresh token à la réponse de façon persistante."""
    jwt_settings = settings.SIMPLE_JWT
    cookie_name = jwt_settings.get('AUTH_COOKIE_REFRESH', 'refresh_token')
    lifetime = jwt_settings.get('REFRESH_TOKEN_LIFETIME')
    max_age = int(lifetime.total_seconds()) if hasattr(lifetime, 'total_seconds') else 86400

    response.set_cookie(
        key=cookie_name,
        value=refresh_token_value,
        max_age=max_age,
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        path=jwt_settings.get('AUTH_COOKIE_PATH', '/'),
    )
    return cookie_name


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            if refresh_token:
                _set_refresh_cookie(response, refresh_token)
                del response.data['refresh']
        return response

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class CookieTokenRefreshSerializer(serializers.Serializer):
    pass # Aucun champ requis dans le corps pour Swagger

class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        refresh_token = request.COOKIES.get(cookie_name)

        if not refresh_token:
            return Response({"detail": "Refresh token manquant dans les cookies."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        access = serializer.validated_data.get('access')
        new_refresh = serializer.validated_data.get('refresh')

        response = Response({'access': str(access)}, status=status.HTTP_200_OK)

        if new_refresh:
            _set_refresh_cookie(response, str(new_refresh))

        return response

