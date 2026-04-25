from rest_framework.routers import DefaultRouter
from api.views.project_views import ProjectViewSet
from api.views.task_views import TaskViewSet
from api.views.user_views import UserViewSet
from api.views.column_views import ColumnViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"users", UserViewSet)
router.register(r"columns", ColumnViewSet, basename="column")
