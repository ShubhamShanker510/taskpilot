from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache

from .tasks import *
from .models import *
from .forms import *
from users.models import *



# Html format for sending mail 

# Create your views here.
@login_required(login_url='/users/login/')
def create_edit_task(request, task_id=None):
    
    if request.user.role == 'employee':
        return redirect('/dashboard/tasks/')

    task=None

    if task_id:
        cache_key=f"task:{task_id}"
        task=cache.get(cache_key)

        if not task:
            print("Tasks db called : ✅")
            task = get_object_or_404(Task, id=task_id)
            cache.set(cache_key, task, timeout=300)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task_obj = form.save(commit=False)

            if task_obj.due_date > task_obj.project.deadline:
                form.add_error('due_date', 'Due date cannot be after the project deadline.')
            else:
                task_obj.save()

                
            send_task_notification_email.delay(
                task_obj.assigned_to.email,
                task_obj.assigned_to.username,
                task_obj.title,
                task_obj.description,
                str(task_obj.due_date)
            )

            if task_id:
                cache.delete(f"task:{task_id}")

            if task:
                messages.success(request, 'Task updated successfully. Email will be sent shortly.')
            else:
                messages.success(request, 'Task created successfully. Email will be sent shortly.')
                    
            return redirect('/dashboard/tasks/')
        else:
            messages.warning(request, "Please enter valid data")
    else:
        form = TaskForm(instance=task)

    return render(request, 'dashboard/create_edit_task.html', {'form': form, 'task': task})

# updating status of task
@login_required(login_url='/users/login/')
def status_update(request, task_id=None):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'in_progress', 'done']:
            task.status = new_status
            task.save()
            messages.success(request, f"Task status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")

        return redirect('/dashboard/tasks/')

    return redirect('/dashboard/tasks/')

# task list
@login_required(login_url='/users/login/')
def task_table(request):
    selected_title = request.GET.get('title', '').strip()
    selected_role = request.GET.get('role', '').strip()
    selected_username = request.GET.get('username', '').strip()
    selected_status = request.GET.get('status', '').strip()

    if request.user.role == 'employee':
        tasks = Task.objects.select_related('project', 'assigned_to').filter(assigned_to=request.user)
    else:
        tasks = Task.objects.select_related('project', 'assigned_to').all()

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

# delete task by id
@login_required(login_url='/users/login/')
def delete_task(request, task_id):

    if request.user.role == 'employee' or request.user.role == 'manager':
        return redirect('/dashboard/tasks/')
    

    task=get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully")
    return redirect('/dashboard/tasks')

# task details by id
@login_required(login_url='/users/login/')
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

# delete comment
@login_required(login_url='/users/login/')
def delete_comment(request, task_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)

    #either admin can delete comment or the user who send that comment
    if comment.author == request.user or request.user.role == 'admin':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    return redirect('task_detail', task_id=task_id)

# edit commenting 
@login_required(login_url='/users/login/')
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