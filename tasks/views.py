from django.shortcuts import render

# Create your views here.
def create_project(request):
    user=request.user

    if not user.role == 'admin' or not user.role == 'manager':
        return redirect('/dashboard/')