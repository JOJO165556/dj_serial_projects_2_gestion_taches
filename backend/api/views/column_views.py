"""
Vues API pour les colonnes Kanban.

ColumnViewSet expose les endpoints CRUD pour les colonnes d'un projet.
Supportes le filtrage par projet via le paramètre de requête `?project=<id>`.
Les tâches associées à chaque colonne sont pré-chargées (prefetch_related)
pour éviter le problème N+1 lors du rendu du board Kanban complet.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from api.permissions import IsProjectMemberOrOwner
from apps.task.models import Column
from api.serializers.column_serializer import ColumnSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        summary="Lister les colonnes d'un projet",
        description=(
            "Retourne toutes les colonnes Kanban d'un projet avec leurs tâches imbriquées. "
            "Filtrer par projet via `?project=<id>`."
        ),
        parameters=[
            OpenApiParameter(
                name="project",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID du projet dont on veut les colonnes.",
                required=False,
            )
        ],
        tags=["Colonnes"],
    ),
    retrieve=extend_schema(
        summary="Détail d'une colonne",
        description="Retourne le détail d'une colonne avec ses tâches.",
        tags=["Colonnes"],
    ),
)
class ColumnViewSet(ReadOnlyModelViewSet):
    """Lecture seule des colonnes Kanban, filtrable par projet."""

    serializer_class = ColumnSerializer
    permission_classes = [IsProjectMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = Column.objects.select_related("project").prefetch_related("tasks")
        if not user or not user.is_authenticated:
            return queryset.none()

        queryset = queryset.filter(project__owner=user) | queryset.filter(project__members=user)
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.distinct()

