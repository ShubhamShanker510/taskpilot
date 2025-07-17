from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Task

@shared_task
def send_task_notification_email(user_email, username, title, description, due_date):
    print("Sending reminder emails...")
    subject = f"You have been assigned a new task: {title}"
    message = f"Hi {username},\n\nYou have a new task: {title}."
    html_message = f"""
    <html>
      <body>
        <h2 style="color:#4CAF50;">Task Assigned</h2>
        <p>Hello <strong>{username}</strong>,</p>
        <p>You have been assigned a new task:</p>
        <ul>
          <li><strong>Title:</strong> {title}</li>
          <li><strong>Description:</strong> {description}</li>
          <li><strong>Due Date:</strong> {due_date}</li>
        </ul>
        <p>Please log in to the portal to start working.</p>
      </body>
    </html>
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        html_message=html_message,
    )

@shared_task
def send_due_soon_reminders():
    today=timezone.now().date()
    target_date= today+timezone.timedelta(days=3)
    due_tasks=Task.objects.filter(due_date=target_date, status__in=["pending", "in_progress"])
    
    for task in due_tasks:
        user = task.assigned_to
        subject = f"Reminder: Task '{task.title}' is due in 3 days"
        message = f"Hi {user.username}, your task '{task.title}' is due on {task.due_date}. Please make sure to complete it on time."

        html_message = f"""
        <html>
            <body>
                <h2 style="color:#f39c12;">Upcoming Task Reminder</h2>
                <p>Hello <strong>{user.username}</strong>,</p>
                <p>This is a reminder for your task:</p>
                <ul>
                    <li><strong>Title:</strong> {task.title}</li>
                    <li><strong>Description:</strong> {task.description}</li>
                    <li><strong>Due Date:</strong> {task.due_date}</li>
                </ul>
                <p>Please ensure it’s completed on time.</p>
            </body>
        </html>
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )