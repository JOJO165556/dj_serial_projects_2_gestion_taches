from rest_framework.viewsets import ModelViewSet
from apps.users.models import User
from api.serializers.user_serializer import UserSerializer
from api.permissions import IsUserSelfOrAdmin
from services.user_service import create_user

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserSelfOrAdmin]
    
    def perform_create(self, serializer):
        user = create_user(**serializer.validated_data)    
        serializer.instance = user