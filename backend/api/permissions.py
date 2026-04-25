from rest_framework.permissions import BasePermission, IsAuthenticated

class IsProjectAllowed(BasePermission):

    def has_permission(self, request, view):
        # Premier niveau : l'utilisateur doit etre authentifie
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_read_only = request.method in ["GET", "HEAD", "OPTIONS"]

        if obj.owner == user:
            if not is_read_only and not obj.is_active:
                if request.method in ["PATCH", "PUT"] and request.data.get("is_active") in [True, "true", "True"]:
                    return True
                return False
            return True

        if user in obj.members.all():
            if is_read_only:
                return True

        return False

class IsTaskAllowed(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        project = obj.project
        is_read_only = request.method in ["GET", "HEAD", "OPTIONS"]

        if not is_read_only and not project.is_active:
            return False

        if project.owner == user:
            return True

        if user in project.members.all():
            if is_read_only:
                return True

        if obj.assigned_to == user and is_read_only:
            return True

        return False


class IsProjectMemberOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        user = request.user
        is_read_only = request.method in ["GET", "HEAD", "OPTIONS"]

        if not is_read_only and not project.is_active:
            return False

        if project.owner == user:
            return True

        if user in project.members.all():
            if is_read_only:
                return True
            return user.role in ["admin", "member"]

        return False

class IsUserSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
