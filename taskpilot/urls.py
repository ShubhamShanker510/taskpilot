"""
URL configuration for taskpilot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import *


urlpatterns = [
    path('', redirect_to_login),
    path('users/', include('users.urls')),
    path('dashboard/', user_profile, name="user_profile"),
    path('dashboard/users/', user_table, name="user_table"),
    path('dashboard/users/create', create_edit_user, name="create_user"),
    path('dashboard/users/<int:user_id>/', create_edit_user, name="edit_user"),
    path('dashboard/users/delete/<int:user_id>', delete_user, name="delete_user"),
    path('admin/', admin.site.urls),
]
