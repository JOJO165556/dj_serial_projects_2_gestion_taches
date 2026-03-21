from apps.project.models import Project

def create_project(name, description, owner, start_date):
    project = Project.objects.create(
        name=name,
        description=description,
        owner=owner,
        start_date=start_date
    )
    return project

def add_member(project, user):
    project.members.add(user)
    return project

def deactivate_project(project):
    project.is_active = False
    project.save()
    return project