from django.core.cache import cache
from django.db.models import Count
from tasks.models import Task
from users.models import CustomUser
from projects.models import Project

def get_dashboard_data():
    dashboard_data = cache.get('dashboard_counts')
    if dashboard_data:
        return dashboard_data

    task_counts = Task.objects.values('status').annotate(count=Count('id'))
    task_count_dict = {'pending': 0, 'done': 0, 'in_progress': 0}
    for item in task_counts:
        task_count_dict[item['status']] = item['count']

    user_counts = CustomUser.objects.values('role').annotate(count=Count('id'))
    user_count_dict = {'admin': 0, 'manager': 0, 'employee': 0}
    for item in user_counts:
        user_count_dict[item['role']] = item['count']

    total_projects = Project.objects.count()

    dashboard_data = {
        'pending_task': task_count_dict['pending'],
        'completed_task': task_count_dict['done'],
        'inprogress_task': task_count_dict['in_progress'],
        'total_admin': user_count_dict['admin'],
        'total_manager': user_count_dict['manager'],
        'total_employee': user_count_dict['employee'],
        'total_projects': total_projects
    }

    cache.set('dashboard_counts', dashboard_data, timeout=300)
    return dashboard_data