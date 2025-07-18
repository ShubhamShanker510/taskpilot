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
from projects. views import *
from tasks.views import *
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', redirect_to_login),
    path('users/', include('users.urls')),
    path('logout/', logout_user, name="logout_user"),
    path('dashboard/profile/', user_profile, name="user_profile"),
    path('dashboard/profile/<int:user_id>/', update_own_profile, name="update_own_profile"),
    path('dashboard/home/', home, name="home"),
    path('dashboard/users/', user_table, name="user_table"),
    path('dashboard/users/create/', create_edit_update_user, name="create_user"),
    path('dashboard/users/edit/<int:user_id>/', create_edit_update_user, name="edit_user"),
    path('dashboard/users/delete/<int:user_id>/', delete_user, name="delete_user"),
    path('dashboard/projects/', project_table, name="project_table"),
    path('dashboard/projects/create/',create_edit_project, name="create_project"),
    path('dashboard/projects/edit/<int:project_id>/',create_edit_project, name="edit_project"),
    path('dashboard/projects/delete/<int:project_id>/',delete_project, name="delete_project"),
    path('dashboard/tasks/', task_table, name='task_table'),
    path('dashboard/tasks/create/', create_edit_task, name='create_task'),
    path('dashboard/tasks/<int:task_id>/',task_detail, name="task_detail" ),
    path('dashboard/tasks/<int:task_id>/edit/<int:comment_id>', edit_comment, name="edit_comment"),
    path('dashboard/tasks/<int:task_id>/delete/<int:comment_id>', delete_comment, name="delete_comment"),
    path('dashboard/tasks/edit/<int:task_id>/', create_edit_task, name='edit_task'),
    path('dashboard/tasks/delete/<int:task_id>/', delete_task, name='delete_task'),
    path('dashboard/tasks/status-update/<int:task_id>/', status_update, name='status_update'),
    # path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)