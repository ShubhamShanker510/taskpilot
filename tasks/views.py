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
@login_required
def create_edit_task(request, task_id=None):
    task = get_object_or_404(Task, id=task_id) if task_id else None

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()

            if task:
                messages.success(request, 'Task updated successfully.')
            else:
                messages.success(request, "Task created successfully")
            
            return redirect('/dashboard/tasks/')
        else:
            messages.warning(request, "Please enter a valid data")
    else:
        form = TaskForm(instance=task)

    return render(request, 'dashboard/create_edit_task.html', {'form': form, 'task': task})

@login_required
def task_table(request):
    selected_title = request.GET.get('title', '').strip()
    selected_role = request.GET.get('role', '').strip()
    selected_username = request.GET.get('username', '').strip()
    selected_status = request.GET.get('status', '').strip()

    tasks = Task.objects.select_related('project', 'assigned_to')

    if selected_title:
        tasks = tasks.filter(project__name__icontains=selected_title)
        messages.info(request, f"Filtered by title: {selected_title}")

    if selected_role:
        tasks = tasks.filter(assigned_to__role=selected_role)
        messages.info(request, f"Filtered by role: {selected_role}")

    if selected_username:
        tasks = tasks.filter(assigned_to__username__icontains=selected_username)
        messages.info(request, f"Filtered by username: {selected_username}")

    if selected_status:
        tasks = tasks.filter(status=selected_status)
        messages.info(request, f"Filtered by status: {selected_status}")
    
    tasks=tasks.order_by("id")

    paginator = Paginator(tasks, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    pagecount = tasks.count()

    roles = CustomUser._meta.get_field('role').choices
    statuses = Task._meta.get_field('status').choices

    return render(request, 'dashboard/task_table.html', {
        'tasks': page,
        'page_obj': page,
        'taskcount': pagecount,
        'selected_title': selected_title,
        'selected_role': selected_role,
        'selected_username': selected_username,
        'selected_status': selected_status,
        'roles': roles,
        'statuses': statuses,
    })


@login_required
def delete_task(request, task_id):
    task=get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully")
    return redirect('/dashboard/tasks')

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all()
    form = CommentForm()
    editing_comment = None

    if 'edit' in request.GET:
        editing_comment = get_object_or_404(Comment, id=request.GET.get('edit'), task=task)
        form = CommentForm(instance=editing_comment)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.task = task
            new_comment.author = request.user
            new_comment.save()
            return redirect('task_detail', task_id=task_id)

    return render(request, 'dashboard/task_detail.html', {
        'task': task,
        'comments': comments,
        'form': form,
        'editing_comment': editing_comment,
    })


@login_required
def delete_comment(request, task_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)
    if comment.author == request.user or request.user.role == 'admin':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    return redirect('task_detail', task_id=task_id)


@login_required
def edit_comment(request, task_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)

    if comment.author != request.user and request.user.role != 'admin':
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect('task_detail', task_id=task_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect('task_detail', task_id=task_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'dashboard/edit_comment.html', {
        'form': form,
        'task': comment.task,
        'comment': comment
    })