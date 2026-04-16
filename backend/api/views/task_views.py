from rest_framework.viewsets import ModelViewSet
from apps.task.models import Task
from api.serializers.task_serializer import TaskSerializer
from api.permissions import IsTaskAllowed
from services.task_service import create_task, assign_task, change_status

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsTaskAllowed]
    
    def perform_create(self, serializer):
        create_task(
            project=serializer.validated_data["project"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            priority=serializer.validated_date.get("priority", "medium")
        )
        
    def perform_update(self, serializer):
        task = self.get_object()
        
        status = serializer.validated_data.get("status")
        assigned_to = serializer.validated_data.get("assigned_to")
        
        if status:
            change_status(task, status)
            
        if assigned_to:
            assign_task(task, assigned_to)
            
        serializer.save()