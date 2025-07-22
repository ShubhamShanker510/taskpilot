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
from users.views import home_views, user_views
from projects.views import project_views
from tasks.views import task_views, comment_views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', home_views.redirect_to_login),
    path('users/', include('users.urls')),
    path('logout/', user_views.logout_user.as_view(), name="logout_user"),
    path('dashboard/profile/', user_views.user_profile.as_view(), name="user_profile"),
    path('dashboard/profile/<int:user_id>/', user_views.update_own_profile.as_view(), name="update_own_profile"),
    path('dashboard/home/', home_views.home, name="home"),
    path('dashboard/users/', user_views.user_table.as_view(), name="user_table"),
    path('dashboard/users/create/', user_views.create_edit_update_user.as_view(), name="create_user"),
    path('dashboard/users/edit/<int:user_id>/', user_views.create_edit_update_user.as_view(), name="edit_user"),
    path('dashboard/users/delete/<int:user_id>/', user_views.delete_user.as_view(), name="delete_user"),
    path('dashboard/projects/', project_views.project_table.as_view(), name="project_table"),
    path('dashboard/projects/create/',project_views.create_edit_project.as_view(), name="create_project"),
    path('dashboard/projects/edit/<int:project_id>/',project_views.create_edit_project.as_view(), name="edit_project"),
    path('dashboard/projects/delete/<int:project_id>/',project_views.delete_project.as_view(), name="delete_project"),
    path('dashboard/tasks/', task_views.task_table.as_view(), name='task_table'),
    path('dashboard/tasks/create/', task_views.create_edit_task.as_view(), name='create_task'),
    path('dashboard/tasks/<int:task_id>/',task_views.task_detail.as_view(), name="task_detail" ),
    path('dashboard/tasks/<int:task_id>/edit/<int:comment_id>', comment_views.edit_comment, name="edit_comment"),
    path('dashboard/tasks/<int:task_id>/delete/<int:comment_id>', comment_views.delete_comment, name="delete_comment"),
    path('dashboard/tasks/edit/<int:task_id>/', task_views.create_edit_task.as_view(), name='edit_task'),
    path('dashboard/tasks/delete/<int:task_id>/', task_views.delete_task.as_view(), name='delete_task'),
    path('dashboard/tasks/status-update/<int:task_id>/', task_views.status_update.as_view(), name='status_update'),
    # path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)