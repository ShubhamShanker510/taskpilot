from django.db import models
from django.conf import settings


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField(null=True, blank=True)  # <-- Added deadline
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Projects"

    def __str__(self):
        return self.name