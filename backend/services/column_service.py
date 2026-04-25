"""
Service de gestion des colonnes Kanban.

Fournit les fonctions pour créer, configurer et initialiser les colonnes
d'un tableau Kanban associé à un projet. Les colonnes par défaut (A faire,
En cours, Termine) sont automatiquement créées à la création d'un projet.
"""

from apps.task.models import Column


DEFAULT_COLUMNS = [
    {"name": "A faire", "order": 0, "color": "#94a3b8"},
    {"name": "En cours", "order": 1, "color": "#6366f1"},
    {"name": "Termine", "order": 2, "color": "#22c55e"},
]


def create_column(project, name, order, color="#6366f1"):
    """Crée une colonne personnalisée pour un projet."""
    return Column.objects.create(
        project=project,
        name=name,
        order=order,
        color=color,
    )


def create_default_columns(project):
    """Crée les colonnes par défaut lors de la création d'un projet."""
    return [
        Column.objects.create(project=project, **col)
        for col in DEFAULT_COLUMNS
    ]
