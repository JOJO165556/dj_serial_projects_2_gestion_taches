from rest_framework.permissions import BasePermission

class IsProjectAllowed(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if obj.owner == user:
            return True
        
        if user in obj.members.all():
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return True
        
        return False
    
class IsTaskAllowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        project = obj.project

        if project.owner == user:
            return True
        
        if user in project.members.all():
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return True
            
        if obj.assigned_to == user:
            return True
            
        return False
    
class IsUserSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
    