from rest_framework.routers import DefaultRouter
from api.views.project_views import ProjectViewSet
from api.views.task_views import TaskViewSet
from api.views.user_views import UserViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"users", UserViewSet)

urlpatterns = router.urls