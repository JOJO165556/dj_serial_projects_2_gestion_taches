from django.urls import re_path
from api import consumers

websocket_urlpatterns = [
    re_path(r"ws/kanban/(?P<project_id>\d+)/$", consumers.KanbanConsumer.as_asgi()),
]
