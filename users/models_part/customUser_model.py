from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    image = CloudinaryField(
        "image",
        default="https://res.cloudinary.com/damhf0l6i/image/upload/v1752740783/profile_fovdcg.webp",
    )
    bio = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Users"
        indexes = [
            models.Index(fields=["role", "is_superuser"]),
        ]
