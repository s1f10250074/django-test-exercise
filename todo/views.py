from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Project, Task


# Create your views here.
def index(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name', '').strip()
        project = None

        if project_name:
            project, created = Project.objects.get_or_create(name=project_name)
        else:
            project_id = request.POST.get('project')
            if project_id:
                project = Project.objects.get(pk=project_id)

        due_at = request.POST.get('due_at')
        
        task = Task(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            due_at=make_aware(parse_datetime(due_at)) if due_at else None,
            project=project,
        )
        
        task.save()

    tasks = Task.objects.all()

    if request.GET.get('filter') == 'active':
        tasks = tasks.filter(completed=False)

    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    projects = Project.objects.order_by('name')

    context = {
        "tasks": tasks,
        "projects": projects,
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
        'project': task.project,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == 'POST':
        project_name = request.POST.get('project_name', '').strip()
        project = None

        if project_name:
            project, created = Project.objects.get_or_create(name=project_name)
        else:
            project_id = request.POST.get('project')
            if project_id:
                project = Project.objects.get(pk=project_id)

        task.title = request.POST['title']

        task.description = request.POST.get('description', '')
        task.due_at = make_aware(parse_datetime(request.POST['due_at'])) if request.POST.get('due_at') else None
        task.project = project

        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task,
        'projects': Project.objects.order_by('name'),
    }
    return render(request, "todo/edit.html", context)


def project_list(request):
    projects = Project.objects.order_by('name')
    project_data = []
    for project in projects:
        tasks = project.tasks.all()
        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        project_data.append({
            'project': project,
            'total': total,
            'completed': completed,
            'progress': int(completed / total * 100) if total else 0,
        })

    context = {
        'projects': project_data,
    }
    return render(request, 'todo/project_list.html', context)


def project_detail(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")

    tasks = Task.objects.filter(project=project).order_by('-posted_at')
    total = tasks.count()
    completed = tasks.filter(completed=True).count()
    context = {
        'project': project,
        'tasks': tasks,
        'total': total,
        'completed': completed,
        'progress': int(completed / total * 100) if total else 0,
    }
    return render(request, 'todo/project_detail.html', context)


def project_update(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")

    if request.method == 'POST':
        project.name = request.POST.get('name', '').strip()
        project.save()
        return redirect(project_detail, project_id)

    context = {
        'project': project,
    }
    return render(request, 'todo/project_edit.html', context)


def project_delete(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")

    if request.method == 'POST':
        project.delete()
        return redirect(project_list)

    context = {
        'project': project,
    }
    return render(request, 'todo/project_delete.html', context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.completed = not task.completed
    task.save()
    return redirect(detail, task_id)

