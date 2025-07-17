import cloudinary.uploader
import os
from celery import shared_task
from django.shortcuts import get_object_or_404
from .models import *

@shared_task
def upload_user_image_to_cloudinary(user_id, image_path):
    try:
        user=get_object_or_404(CustomUser, id=user_id)
        upload_result=cloudinary.uploader.upload(image_path)

        # Update the image field with cloudinary url
        user.image=upload_result['secure_url']
        user.save()

        # delete local image after upload
        if os.path.exists(image_path):
            os.remove(image_path)
    
    except CustomUser.DoesNotExist:
        pass
    except Exception as e:
        # Optional: log or print error
        print(f"Error uploading image for user {user_id}: {str(e)}")

