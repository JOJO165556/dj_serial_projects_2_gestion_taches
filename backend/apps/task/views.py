from django.shortcuts import render, redirect, get_object_or_404
from apps.task.models import Task
from apps.project.models import Project
from services.task_service import create_task

from apps.users.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def task_list(request):
    # Liste tâches
    if request.user.role == 'admin':
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(project__members=request.user)
    return render(request, "task/list.html", {"tasks": tasks})

@login_required
def task_detail(request, pk):
    # Détail tâche
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role != 'admin' and request.user not in task.project.members.all():
        return redirect("task_list")
    
    return render(request, "task/detail.html", {"task": task})

@login_required
def task_create(request):
    # Création tâche
    if request.user.role == 'reader':
        return redirect("task_list")
        
    if request.method == "POST":
        project_obj = get_object_or_404(Project, pk=request.POST.get("project"))
        task = create_task(
            project=project_obj,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            priority=request.POST.get("priority", "medium"),
        )
        
        assigned_to_id = request.POST.get("assigned_to")
        if assigned_to_id:
            assigned_user = get_object_or_404(User, pk=assigned_to_id)
            task.assigned_to = assigned_user
            if assigned_user not in project_obj.members.all():
                project_obj.members.add(assigned_user)
            if assigned_user.role == 'reader':
                assigned_user.role = 'member'
                assigned_user.save()
            
        status = request.POST.get("status")
        if status:
            task.status = status
            
        task.save()
        return redirect("task_list")
    
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    users = User.objects.all()
    return render(request, "task/form.html", {"projects": projects, "users": users})

@login_required
def task_edit(request, pk):
    # Édition tâche
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role == 'reader':
        return redirect("task_detail", pk=task.pk)
        
    if request.user not in task.project.members.all() and request.user != task.project.owner:
        return redirect("task_list")
        
    if request.method == "POST":
        project_id = request.POST.get("project")
        if project_id:
            task.project = get_object_or_404(Project, pk=project_id)
            
        task.title = request.POST.get("title", task.title)
        task.description = request.POST.get("description", task.description)
        task.priority = request.POST.get("priority", task.priority)
        task.status = request.POST.get("status", task.status)
        
        assigned_to_id = request.POST.get("assigned_to")
        if assigned_to_id:
            assigned_user = get_object_or_404(User, pk=assigned_to_id)
            task.assigned_to = assigned_user
            if assigned_user not in task.project.members.all():
                task.project.members.add(assigned_user)
            if assigned_user.role == 'reader':
                assigned_user.role = 'member'
                assigned_user.save()
            
        task.save()
        return redirect("task_detail", pk=task.pk)
        
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    users = User.objects.all()
    return render(request, "task/form.html", {"task": task, "projects": projects, "users": users})