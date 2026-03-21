from apps.task.models import Task

def create_task(project, title, description, priority="medium"):
    return Task.objects.create(
        project=project,
        title=title,
        description=description,
        priority=priority
    )
    
def assign_task(task, user):
    task.assigned_to = user
    task.save()
    return task

def change_status(task, status):
    if task.status == status:
        return task
    
    task.status = status
    task.save()
    return task