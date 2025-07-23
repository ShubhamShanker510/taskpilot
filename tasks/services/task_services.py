from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.paginator import Paginator


from ..models import Task, Comment
from users.models import CustomUser
from ..tasks import send_task_notification_email


def get_task_with_cache(task_id):
    cache_key=f"task:{task_id}"
    task=cache.get(cache_key)

    if not task:
        print("Tasks db called : ✅")
        task = get_object_or_404(Task.objects.select_related('assigned_to', 'project'), id=task_id)
        cache.set(cache_key, task, timeout=300)

    return task

def save_task_and_notify(task_obj, task_id=None):
    task_obj.save()
    cache.delete("dashboard_counts")

    send_task_notification_email.delay(
        task_obj.assigned_to.email,
        task_obj.assigned_to.username,
        task_obj.title,
        task_obj.description,
        str(task_obj.due_date)
    )

    if task_id:
        cache.delete(f"task:{task_id}")

def update_task_status(task, new_status):
    task.status=new_status
    task.save()
    cache.delete("dashboard_counts")

def get_filtered_tasks(user, filters, page_number, per_page=5):
    selected_title = filters.get('title', '').strip()
    selected_role = filters.get('role', '').strip()
    selected_username = filters.get('username', '').strip()
    selected_status = filters.get('status', '').strip()

    # Base queryset
    if user.role == 'employee':
        tasks = Task.objects.select_related('project', 'assigned_to').filter(assigned_to=user)
    else:
        tasks = Task.objects.select_related('project', 'assigned_to').all()

    # Filtering
    if selected_title:
        tasks = tasks.filter(project__name__icontains=selected_title)

    if selected_role:
        tasks = tasks.filter(assigned_to__role=selected_role)

    if selected_username:
        tasks = tasks.filter(assigned_to__username__icontains=selected_username)

    if selected_status:
        tasks = tasks.filter(status=selected_status)

    # Sorting
    tasks = tasks.order_by("id")

    # Pagination
    paginator = Paginator(tasks, per_page)
    page = paginator.get_page(page_number)

    return {
        'page': page,
        'count': paginator.count,
        'roles': CustomUser._meta.get_field('role').choices,
        'statuses': Task._meta.get_field('status').choices,
    }