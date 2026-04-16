from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.project.models import Project
from api.serializers.project_serializer import ProjectSerializer
from api.permissions import IsProjectAllowed
from services.project_service import create_project, add_member, deactivate_project

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectAllowed]
    
    def perform_create(self, serializer):
        project = create_project(
            name=serializer.validated_data["name"],
            description=serializer.validated_data["description"],
            owner=self.request.user,
            start_date=serializer.validated_data["start_date"]
        )
        
        serializer.instance = project
    
    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()
        
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        
        add_member(project, user)
        return Response({"message": "member added"})
        
    def perform_update(self, serializer):
        project = self.get_object()
    
        if "is_active" in serializer.validated_data:
            if serializer.validated_data.get("is_active") is False:
                deactivate_project(project)
                return
                        
        serializer.save()