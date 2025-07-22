from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from ..models import *
from ..forms import *
from users.models import *
from ..services import project_services


# create and edit project
@login_required(login_url='/users/login/')
def create_edit_project(request, project_id=None):
    project=project_services.get_project_by_id_with_cache(project_id) if project_id else None

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

    filters={
        'title': request.GET.get('title', '').strip(),
        'role': request.GET.get('role', '').strip(),
        'username': request.GET.get('username', '').strip(),
    }
    
    page_number = request.GET.get('page')

    data=project_services.get_filtered_projects(filters, page_number)

    for key, value in filters.items():
        if value.strip():
            messages.info(request, f"Filtered by {key}: {value.strip()}")

    return render(request, 'dashboard/project_table.html', {
        'projects': data['page'],  
        'page_obj': data['page'],
        'pagecount': data['pagecount'],
        'selected_title': filters['title'],
        'selected_role': filters['role'],
        'selected_username': filters['username'],
        'roles': data['roles'],
    })


# delete project by admin
@login_required(login_url='/users/login/')
def delete_project(request, project_id):
    if request.user.role == 'admin':
        project=get_object_or_404(Project.objects.select_related('created_by'), id=project_id)
        project.delete()
        messages.success(request, "Project deleted successfully")
        cache.delete('dashboard_counts')
        return redirect('/dashboard/projects/')
    elif request.user.role =='manager':
        return redirect('/dashboard/projects/')