from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from api.serializers.user_serializer import UserSerializer, RegisterSerializer
from api.permissions import IsUserSelfOrAdmin
from services.user_service import create_user, update_user
from django.contrib.auth import get_user_model

User = get_user_model()

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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)