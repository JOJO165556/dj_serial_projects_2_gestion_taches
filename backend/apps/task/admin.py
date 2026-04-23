"""
Admin configuration pour l'application task.

Enregistre les modèles Task et Column dans l'interface d'administration Django
avec des options d'affichage, de filtrage et de recherche adaptées au Kanban.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Column, Task


@admin.register(Column)
class ColumnAdmin(ModelAdmin):
    """
    Administration des colonnes Kanban.

    Permet de visualiser et gérer les colonnes de chaque projet,
    leur nom, leur ordre d'affichage et leur couleur.
    """

    list_display = ("name", "project", "order", "color")
    list_filter = ("project",)
    ordering = ("project", "order")
    search_fields = ("name", "project__name")


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    """
    Administration des tâches.

    Affiche les tâches avec leur colonne Kanban, leur priorité et leur projet.
    Permet de filtrer par colonne et priorité, et de rechercher par titre.
    """

    list_display = ("title", "column", "priority", "project", "assigned_to")
    list_filter = ("column", "priority")
    search_fields = ("title", "project__name")
    autocomplete_fields = ("column",)
