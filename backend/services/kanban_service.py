from django.db.models import Case, When, Value, IntegerField
from api.serializers.task_serializer import TaskSerializer
from api.serializers.project_serializer import ProjectSerializer

def get_full_kanban_board(project):
    # 1 Recuperer les colonnes
    columns = project.columns.all().order_by('order')
    columns_data = [{"id": col.id, "name": col.name, "order": col.order, "color": col.color} for col in columns]
    
    # 2 Recuperer les taches avec tri combine par score de priorite puis position
    tasks = project.tasks.select_related("assigned_to", "column").annotate(
        priority_score=Case(
            When(priority='high', then=Value(1)),
            When(priority='medium', then=Value(2)),
            When(priority='low', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('priority_score', 'position')
    
    # Serialiser les taches
    tasks_data = TaskSerializer(tasks, many=True).data
    
    # 3 Grouper par id de colonne
    board = {col.id: [] for col in columns}
    board["unassigned"] = []
    
    for task in tasks_data:
        col_id = task.get("column")
        if col_id in board:
            board[col_id].append(task)
        else:
            board["unassigned"].append(task)
            
    # Supprimer le groupe non assigne si vide
    if not board["unassigned"]:
        del board["unassigned"]

    return {
        "project": ProjectSerializer(project).data,
        "columns": columns_data,
        "board": board
    }
