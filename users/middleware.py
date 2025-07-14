from django.shortcuts import redirect
from django.contrib import messages

class HandleLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/users/login/':
            if request.user.is_authenticated:
                user = request.user

                # Check if user has a known role
                if hasattr(user, 'role') and user.role in ['admin', 'manager', 'employee']:
                    return redirect('/dashboard/')
                else:
                    messages.error(request, "Unkown user.")
                    return redirect('/users/login/')
            # else:
            #     return redirect('/users/login/')

        return self.get_response(request)
