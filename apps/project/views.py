from django.shortcuts import render, redirect, get_object_or_404
from apps.project.models import Project
from services.project_service import create_project
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from apps.users.models import User

@login_required
def project_list(request):
    # Liste projets
    if request.user.role == 'admin':
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    return render(request, "project/list.html", {"projects": projects})

@login_required
def project_detail(request, pk):
    # Détail projet
    project = get_object_or_404(Project, pk=pk)
    
    # Vérification stricte des droits d'accès au projet
    if request.user.role != 'admin' and request.user not in project.members.all() and request.user != project.owner:
        return redirect("project_list")
    
    return render(request, "project/detail.html", {"project": project})

@login_required
def project_create(request):
    # Création projet
    if request.user.role == 'reader':
        return redirect("project_list")
        
    if request.method == "POST":
        owner_user = request.user
        
        project = create_project(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            owner=owner_user,
            start_date=request.POST.get("start_date") or timezone.now()
        )
        
        members_ids = request.POST.getlist("members")
        project.members.set(members_ids)
        if owner_user not in project.members.all():
            project.members.add(owner_user)
            
        # Mise à jour des rôles : un lecteur ajouté à un projet devient membre
        for member in project.members.all():
            if member.role == 'reader':
                member.role = 'member'
                member.save()
            
        return redirect("project_list")
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, "project/form.html", {"users": users})

@login_required
def project_edit(request, pk):
    # Édition projet
    project = get_object_or_404(Project, pk=pk)
    
    # Seul le propriétaire peut modifier le projet
    if request.user != project.owner:
        return redirect("project_list")
        
    if request.method == "POST":
        project.name = request.POST.get("name", project.name)
        project.description = request.POST.get("description", project.description)
        
        if "members" in request.POST:
            project.members.set(request.POST.getlist("members"))
            if project.owner not in project.members.all():
                project.members.add(project.owner)
                
            # Mise à jour des rôles : un lecteur ajouté à un projet devient membre
            for member in project.members.all():
                if member.role == 'reader':
                    member.role = 'member'
                    member.save()
            
        project.save()
        return redirect("project_detail", pk=project.pk)
        
    users = User.objects.exclude(id=project.owner.id)
    return render(request, "project/form.html", {"project": project, "users": users})