from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Project

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("name", "owner", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)