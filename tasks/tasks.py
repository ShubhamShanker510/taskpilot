from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_task_notification_email(user_email, username, title, description, due_date):
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
