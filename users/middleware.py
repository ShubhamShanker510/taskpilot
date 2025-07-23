from django.shortcuts import redirect
from django.contrib import messages

class HandleLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the request is for the login page
        if request.path.startswith('/users/login'):

            if request.user.is_authenticated:
                user = request.user

                # Check if user has a known role
                if hasattr(user, 'role'):
                    if user.role in ['admin', 'manager']:
                        return redirect('/dashboard/home')
                    elif user.role == 'employee':
                        return redirect('/dashboard/tasks')
                    else:
                        messages.error(request, "Unknown user role.")
                        return redirect('/users/logout/') 
                else:
                    messages.error(request, "User role not set.")
                    return redirect('/users/logout/')
        

        elif request.path.startswith('/dashboard/users/'):
            if request.user.role == 'manager':
                return redirect('/dashboard/home/')
            if request.user.role == 'employee':
                return redirect('/dashboard/tasks/')
            
        elif request.path.startswith('/dashboard/projects/'):
            if request.user.role == 'employee':
                return redirect('/dashboard/tasks/')

        return self.get_response(request)
