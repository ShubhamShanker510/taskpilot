from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator

from .models import *
from .forms import *
from users.models import *


# Create your views here.

# create project
@login_required
def create_edit_project(request, project_id=None):
    project=get_object_or_404(Project, id=project_id) if project_id else None
    if request.method=="POST":
        form=createProject(request.POST, instance=project)

        if form.is_valid():
            new_project=form.save(commit=False)

            if not project:
                new_project.created_by=request.user
            
            new_project.save()
            
            if project:
                messages.success(request, "Project updated successfully")
            else:
                messages.success(request, "Project created successfully")
            return redirect('/dashboard/projects')         

    
    else:
        form=createProject(instance=project)

    return render(request, 'dashboard/create_edit_project.html', {'form': form, 'project': project})


@login_required
def project_table(request):
    if hasattr(request.user, 'role') and request.user.role == 'employee':
        return redirect('/dashboard/tasks/')


    selected_title = request.GET.get('title', '').strip()
    selected_role = request.GET.get('role', '').strip()
    selected_username = request.GET.get('username', '').strip()

    projects = Project.objects.all()

    if selected_title:
        projects = projects.filter(name__icontains=selected_title)
        messages.info(request, f"filter by title: {selected_title}")

    if selected_role:
        projects = projects.filter(created_by__role=selected_role)
        messages.info(request, f"filter by title: {selected_role}")

    if selected_username:
        projects = projects.filter(created_by__username__icontains=selected_username)
        messages.info(request, f"filter by title: {selected_username}")

    projects=projects.order_by("id")
    paginator = Paginator(projects, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    pagecount = projects.count()

    roles = CustomUser._meta.get_field('role').choices

    return render(request, 'dashboard/project_table.html', {
        'projects': page,  
        'page_obj': page,
        'pagecount': pagecount,
        'selected_title': selected_title,
        'selected_role': selected_role,
        'selected_username': selected_username,
        'roles': roles,
    })


@login_required
def delete_project(request, project_id):
    project=get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully")
    return redirect('/dashboard/projects/')    