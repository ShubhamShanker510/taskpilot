from django.urls import path
from .views import *

app_name="users"

urlpatterns=[
    path('login/', login_user, name="login_user")
]