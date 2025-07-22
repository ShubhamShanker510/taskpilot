from django.shortcuts import get_object_or_404
from ..models import Comment

def get_comment_for_task(task,comment_id):
    return get_object_or_404(Comment.objects.select_related('author'), id=comment_id, task=task)

def can_edit_or_delete_comment(comment, user):
    return comment.author == user or user.role == "admin"