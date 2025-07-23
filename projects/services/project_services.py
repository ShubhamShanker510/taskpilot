from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from users.models import CustomUser

from ..models import Project


def get_project_by_id_with_cache(project_id):
    cache_key = f"project:{project_id}"
    project = cache.get(cache_key)
    if not project:
        print("Projects db called : ✅")
        project = get_object_or_404(
            Project.objects.select_related("created_by"), id=project_id
        )
        cache.set(cache_key, project, timeout=300)
    return project


def get_filtered_projects(filters, page_number, per_page=5):
    selected_title = filters.get("title", "").strip()
    selected_role = filters.get("role", "").strip()
    selected_username = filters.get("username", "").strip()

    projects = Project.objects.select_related("created_by").all()

    if selected_title:
        projects = projects.filter(name__icontains=selected_title)

    if selected_role:
        projects = projects.filter(created_by__role=selected_role)

    if selected_username:
        projects = projects.filter(created_by__username__icontains=selected_username)

    projects = projects.order_by("id")
    paginator = Paginator(projects, per_page)
    page = paginator.get_page(page_number)

    return {
        "page": page,
        "pagecount": paginator.count,
        "roles": CustomUser._meta.get_field("role").choices,
    }
