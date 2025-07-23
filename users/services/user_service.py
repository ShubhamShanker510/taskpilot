import os

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from users.models import CustomUser
from users.tasks import upload_user_image_to_cloudinary


def get_user_by_id(user_id):
    cache_key = f"user:{user_id}"
    user = cache.get(cache_key)
    if not user:
        user = get_object_or_404(CustomUser, id=user_id)
        cache.set(cache_key, user, timeout=300)
    return user


def handle_user_image_upload(user, image):
    if not user:
        return
    if image:
        image_name = f"profile_images/{user.username}_{image.name}"
        image_path = os.path.join(settings.MEDIA_ROOT, image_name)
        with open(image_path, "wb+") as dest:
            for chunk in image.chunks():
                dest.write(chunk)
        upload_user_image_to_cloudinary.delay(user.id, image_path)
