"""
Vues API pour les colonnes Kanban.

ColumnViewSet expose les endpoints CRUD pour les colonnes d'un projet.
Supportes le filtrage par projet via le paramètre de requête `?project=<id>`.
Les tâches associées à chaque colonne sont pré-chargées (prefetch_related)
pour éviter le problème N+1 lors du rendu du board Kanban complet.
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
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
    create=extend_schema(
        summary="Créer une colonne",
        description="Crée une nouvelle colonne dans un projet Kanban.",
        tags=["Colonnes"],
    ),
    retrieve=extend_schema(
        summary="Détail d'une colonne",
        description="Retourne le détail d'une colonne avec ses tâches.",
        tags=["Colonnes"],
    ),
    update=extend_schema(
        summary="Mettre à jour une colonne",
        description="Met à jour le nom, l'ordre ou la couleur d'une colonne.",
        tags=["Colonnes"],
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'une colonne",
        tags=["Colonnes"],
    ),
    destroy=extend_schema(
        summary="Supprimer une colonne",
        description="Supprime la colonne et toutes ses tâches associées.",
        tags=["Colonnes"],
    ),
)
class ColumnViewSet(ModelViewSet):
    """CRUD des colonnes Kanban, filtrable par projet."""

    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Column.objects.select_related("project").prefetch_related("tasks")
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

