from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView

from users.models import *

from ..forms import *
from ..models_parts import *
from ..services import comment_services, task_services
from ..tasks import *


class create_edit_task(LoginRequiredMixin, View):
    template_name = "dashboard/create_edit_task.html"
    login_url = "/users/login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == "employee":
            return redirect("/dashboard/tasks/")
        return super().dispatch(request, *args, **kwargs)

    def get_task(self, task_id=None):
        return task_services.get_task_with_cache(task_id) if task_id else None

    def get(self, request, task_id=None):
        task = self.get_task(task_id)
        form = TaskForm(instance=task)

        return render(self.request, self.template_name, {"form": form, "task": task})

    def post(self, request, task_id=None):
        task = self.get_task(task_id)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task_obj = form.save(commit=False)

            if task_obj.due_date > task_obj.project.deadline:
                form.add_error(
                    "due_date", "Due date cannot be after the project deadline."
                )
            else:
                task_services.save_task_and_notify(task_obj, task_id)

                if task:
                    messages.success(
                        request,
                        "Task updated successfully. Email will be sent shortly.",
                    )
                else:
                    messages.success(
                        request,
                        "Task created successfully. Email will be sent shortly.",
                    )

            return redirect("/dashboard/tasks/")
        else:
            messages.warning(request, "Please enter valid data")

        return render(self.request, self.template_name, {"form": form, "task": task})


# @login_required(login_url='/users/login/')
# def create_edit_task(request, task_id=None):

#     if request.user.role == 'employee':
#         return redirect('/dashboard/tasks/')

#     task=task_services.get_task_with_cache(task_id) if task_id else None

#     if request.method == 'POST':
#         form = TaskForm(request.POST, instance=task)
#         if form.is_valid():
#             task_obj = form.save(commit=False)

#             if task_obj.due_date > task_obj.project.deadline:
#                 form.add_error('due_date', 'Due date cannot be after the project deadline.')
#             else:
#                 task_services.save_task_and_notify(task_obj, task_id)

#                 if task:
#                     messages.success(request, 'Task updated successfully. Email will be sent shortly.')
#                 else:
#                     messages.success(request, 'Task created successfully. Email will be sent shortly.')

#             return redirect('/dashboard/tasks/')
#         else:
#             messages.warning(request, "Please enter valid data")
#     else:
#         form = TaskForm(instance=task)

#     return render(request, 'dashboard/create_edit_task.html', {'form': form, 'task': task})


# updating status of task
class status_update(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, task_id):
        return redirect("/dashboard/tasks/")

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        new_status = request.POST.get("status")

        if new_status in ["pending", "in_progress", "done"]:
            task.status = new_status
            task.save()
            cache.delete("dashboard_counts")
            messages.success(request, f"Task status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")

        return redirect("/dashboard/tasks/")


# @login_required(login_url='/users/login/')
# def status_update(request, task_id=None):
#     task = get_object_or_404(Task.objects.select_related('assigned_to', 'project'), id=task_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')

#         if new_status in ['pending', 'in_progress', 'done']:
#             task.status = new_status
#             task.save()
#             cache.delete('dashboard_counts')
#             messages.success(request, f"Task status updated to {new_status}.")
#         else:
#             messages.error(request, "Invalid status.")

#         return redirect('/dashboard/tasks/')

#     return redirect('/dashboard/tasks/')


# task list
class task_table(LoginRequiredMixin, View):
    login_url = "/users/login/"
    template_name = "dashboard/task_table.html"

    def get(self, request):
        filters = {
            "title": request.GET.get("title", "").strip(),
            "role": request.GET.get("role", "").strip(),
            "username": request.GET.get("username", "").strip(),
            "status": request.GET.get("status", "").strip(),
        }
        page_number = request.GET.get("page")

        data = task_services.get_filtered_tasks(request.user, filters, page_number)

        for key, value in filters.items():
            if value:
                messages.info(request, f"Filtered by {key}: {value}")

        context = {
            "tasks": data["page"],
            "page_obj": data["page"],
            "taskcount": data["count"],
            "selected_title": filters["title"],
            "selected_role": filters["role"],
            "selected_username": filters["username"],
            "selected_status": filters["status"],
            "roles": data["roles"],
            "statuses": data["statuses"],
        }
        return render(request, self.template_name, context)


# @login_required(login_url='/users/login/')
# def task_table(request):

#     filters={
#         'title': request.GET.get('title', '').strip(),
#         'role': request.GET.get('role', '').strip(),
#         'username': request.GET.get('username', '').strip(),
#         'status' : request.GET.get('status', '').strip()
#     }
#     page_number = request.GET.get('page')

#     data=task_services.get_filtered_tasks(request.user, filters, page_number)

#     for key, value in filters.items():
#         if value.strip():
#             messages.info(request, f"Filtered by {key}: {value.strip()}")


#     return render(request, 'dashboard/task_table.html', {
#         'tasks': data['page'],
#         'page_obj': data['page'],
#         'taskcount': data['count'],
#         'selected_title': filters['title'],
#         'selected_role': filters['role'],
#         'selected_username': filters['username'],
#         'selected_status': filters['status'],
#         'roles': data['roles'],
#         'statuses': data['statuses'],
#     })


# delete task by id
class delete_task(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == "manager":
            return redirect("/dashboard/home/")

        if request.user.role == "employee":
            return redirect("/dashboard/tasks/")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, task_id):

        selected_page = request.GET.get("page", 1)
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        messages.success(request, "task deleted successfully")
        cache.delete("dashboard_counts")
        return redirect(f"/dashboard/tasks/?page={selected_page}")


# @login_required(login_url='/users/login/')
# def delete_task(request, task_id):

#     if request.user.role == 'employee' or request.user.role == 'manager':
#         return redirect('/dashboard/tasks/')


#     task=get_object_or_404(Task.objects.select_related('assigned_to', 'project'), id=task_id)
#     task.delete()
#     messages.success(request, "Task deleted successfully")
#     cache.delete('dashboard_counts')
#     return redirect('/dashboard/tasks')


# task details by id
class task_detail(LoginRequiredMixin, View):
    login_url = "/users/login/"
    template_name = "dashboard/task_detail.html"

    def get(self, request, task_id):
        task = get_object_or_404(
            Task.objects.select_related("assigned_to", "project"), id=task_id
        )
        comments = task.comments.select_related("author").all()
        editing_comment = None

        edit_id = request.GET.get("edit")
        if edit_id:
            editing_comment = comment_services.get_comment_for_task(task, edit_id)
            form = CommentForm(instance=editing_comment)
        else:
            form = CommentForm()

        return render(
            request,
            self.template_name,
            {
                "task": task,
                "comments": comments,
                "form": form,
                "editing_comment": editing_comment,
            },
        )

    def post(self, request, task_id):
        task = get_object_or_404(
            Task.objects.select_related("assigned_to", "project"), id=task_id
        )
        form = CommentForm(request.POST)
        comments = task.comments.select_related("author").all()

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.task = task
            new_comment.author = request.user
            new_comment.save()
            return redirect("task_detail", task_id=task_id)

        # If form is invalid, show the same page with errors
        return render(
            request,
            self.template_name,
            {"task": task, "comments": comments, "form": form, "editing_comment": None},
        )


# @login_required(login_url='/users/login/')
# def task_detail(request, task_id):
#     task = get_object_or_404(Task.objects.select_related('assigned_to', 'project'), id=task_id)
#     comments = task.comments.select_related('author').all()
#     form = CommentForm()
#     editing_comment = None

#     if 'edit' in request.GET:
#         editing_comment = comment_services.get_comment_for_task(task, request.GET.get('edit'))
#         form = CommentForm(instance=editing_comment)

#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             new_comment = form.save(commit=False)
#             new_comment.task = task
#             new_comment.author = request.user
#             new_comment.save()
#             return redirect('task_detail', task_id=task_id)

#     return render(request, 'dashboard/task_detail.html', {
#         'task': task,
#         'comments': comments,
#         'form': form,
#         'editing_comment': editing_comment,
#     })
