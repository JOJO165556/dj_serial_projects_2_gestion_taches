from django import forms
from backend.apps.task.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["project", "title", "description", "priority"]