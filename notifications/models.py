from django.db import models
from django.conf import settings

# Create your models here.

class Notifications(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notifications'
    )
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="notifications"
        ordering=['-created_at']

    def __str__(self):
        return f"Notifications for {self.user.username}"