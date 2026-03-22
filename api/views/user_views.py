from rest_framework.viewsets import ModelViewSet
from apps.users.models import User
from api.serializers.user_serializer import UserSerializer
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