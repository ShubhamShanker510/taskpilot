from django.urls import path
from .views import user_views

app_name="users"

urlpatterns=[
    path('login/', user_views.login_user, name="login_user")
]