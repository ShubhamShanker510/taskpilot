from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from ..services import dashboard_service



# custom redirect to login
def redirect_to_login(request):
    return redirect('/users/login')

@login_required(login_url='/users/login/')
def home(request):

    if hasattr(request.user, 'role') and request.user.role == 'employee':
        return redirect('/dashboard/tasks/')
    
    dashboard_data=dashboard_service.get_dashboard_data()
    return render(request, 'dashboard/home.html', dashboard_data)



