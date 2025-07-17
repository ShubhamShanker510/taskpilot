from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    image = models.ImageField(upload_to='profile_images/', default='profile_images/profile.webp')
    bio = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        db_table="Users"