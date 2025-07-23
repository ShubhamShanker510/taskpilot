from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.models import *

from ..forms import *
from ..models import *
from ..services import comment_services, task_services
from ..tasks import *


# delete comment
@login_required(login_url="/users/login/")
def delete_comment(request, task_id, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("task", "author"),
        id=comment_id,
        task__id=task_id,
    )

    # either admin can delete comment or the user who send that comment
    if comment_services.can_edit_or_delete_comment(comment, request.user):
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    return redirect("task_detail", task_id=task_id)


# edit commenting
@login_required(login_url="/users/login/")
def edit_comment(request, task_id, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("task", "author"),
        id=comment_id,
        task__id=task_id,
    )

    if not comment_services.can_edit_or_delete_comment(comment, request.user):
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("task_detail", task_id=task_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect("task_detail", task_id=task_id)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "dashboard/edit_comment.html",
        {"form": form, "task": comment.task, "comment": comment},
    )
