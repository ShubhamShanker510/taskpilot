from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache

from .models import *
from .forms import *
from users.models import *


# create and edit project
@login_required(login_url='/users/login/')
def create_edit_project(request, project_id=None):
    project=None

    # attempt to cache if editing an exisitng project
    if project_id:
        cache_key=f"project:{project_id}"
        project=cache.get(cache_key)

        if not project:
            print("Projects db called : ✅")
            project=get_object_or_404(Project, id=project_id)
            cache.set(cache_key, project, timeout=300)

    if request.method=="POST":
        form=createProject(request.POST, instance=project)

        if form.is_valid():
            new_project=form.save(commit=False)

            if not project:
                new_project.created_by=request.user
            
            new_project.save()
            cache.delete('dashboard_counts')

            if project_id:
                cache.delete(f"project:{project_id}")
            
            if project:
                messages.success(request, "Project updated successfully")
            else:
                messages.success(request, "Project created successfully")
            return redirect('/dashboard/projects')         

    
    else:
        form=createProject(instance=project)

    return render(request, 'dashboard/create_edit_project.html', {'form': form, 'project': project})


# all project list
@login_required(login_url='/users/login/')
def project_table(request):

    selected_title = request.GET.get('title', '').strip()
    selected_role = request.GET.get('role', '').strip()
    selected_username = request.GET.get('username', '').strip()

    projects = Project.objects.select_related('created_by').all()

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

    pagecount = paginator.count

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


# delete project by admin
@login_required(login_url='/users/login/')
def delete_project(request, project_id):
    if request.user.role == 'admin':
        project=get_object_or_404(Project, id=project_id)
        project.delete()
        messages.success(request, "Project deleted successfully")
        cache.delete('dashboard_counts')
        return redirect('/dashboard/projects/')
    elif request.user.role =='manager':
        return redirect('/dashboard/projects/')