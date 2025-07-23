import os
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy 

from ..models import *
from ..forms import *
from ..tasks import *
from tasks.models_parts import *
from projects.models import *
from ..services import  user_service


# login form
class login_user(FormView):
    template_name="users/login.html"
    form_class=LoginForm
    success_url=reverse_lazy('dashboard_home')
    login_url='/users/login'

    def form_valid(self, form):
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']
        user=authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, "USer login successfully")

            role=user.role
            if role in ['admin', 'manager']:
                return redirect('/dashboard/home')
            elif role == 'employee':
                return redirect('/dashboard/tasks')
            else:
                messages.error(self.request, "Unauthorized user role")
                return redirect(self.login_url)
        
        else:
            messages.error(self.request, "Invalid username or password0")
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        return super().form_invalid(form)

# def login_user(request):
#     if request.method=="POST":
#         form=LoginForm(request.POST)

#         if form.is_valid():
#             username=form.cleaned_data['username']
#             password=form.cleaned_data['password']

#             user=authenticate(request, username=username, password=password)
            
#             if user is not None:
#                 login(request, user)
#                 messages.success(request,"User Login successfully")
                
#                 if request.user.role == 'admin' or request.user.role == 'manager':
#                     return redirect('/dashboard/home/')
#                 elif request.user.role == 'employee':
#                     return redirect('/dashboard/tasks')
            
#             else:
#                 messages.error(request, "Invalid user")
#         else:
#             messages.error(request, "Please enter valid data")
    
#     else:
#         form=LoginForm()
    
#     return render(request, "users/login.html", {'form':form})


# user profile
class user_profile(LoginRequiredMixin, View):
    template_name = 'dashboard/user_profile.html'
    login_url = '/users/login/'

    def get(self, request):
        context = {
            'user': request.user
        }
        return render(request, self.template_name, context)

#  def user_profile(request):
#     user=request.user

#     return render(request, 'dashboard/user_profile.html', {'user':user})

# user_table
class user_table(LoginRequiredMixin, ListView):
    model=CustomUser
    template_name='dashboard/user_table.html'
    context_object_name='users'
    paginate_by=5
    login_url='/users/login'

    def get_queryset(self):
        queryset = CustomUser.objects.filter(is_superuser=False)
        selected_username = self.request.GET.get('username', '').strip()
        selected_role = self.request.GET.get('role', '').strip()

        if selected_username:
            queryset = queryset.filter(username__icontains=selected_username)

        if selected_role:
            queryset = queryset.filter(role=selected_role)

        # print(queryset)

        return queryset.order_by('id')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role =='manager':
            return redirect('/dashboard/home')
        
        if request.user.role == 'employee':
            return redirect('/dashboard/tasks')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usercount'] = self.get_queryset().count()
        context['selected_username'] = self.request.GET.get('username', '').strip()
        context['selected_role'] = self.request.GET.get('role', '').strip()
        return context


# @login_required(login_url='/users/login/')
# def user_table(request):
#     if request.user.role == 'manager':
#         return redirect('/dashboard/home/')
    
#     if request.user.role == 'employee':
#         return redirect('/dashboard/tasks/')

#     users=CustomUser.objects.filter(is_superuser = False)

#     # filter-searching
#     selected_username=request.GET.get('username', '').strip()
#     selected_role=request.GET.get('role','').strip()

#     if selected_username:
#         users=users.filter(username__icontains=selected_username)
#     elif selected_role:
#         users=users.filter(role=selected_role)

#     users=users.order_by("id")
#     paginator=Paginator(users, 5)
#     page_number=request.GET.get('page')
#     page=paginator.get_page(page_number)
#     usercount=paginator.count

#     return render(request, 'dashboard/user_table.html', {'users': page,'page_obj':page,'usercount':usercount, 'selected_username': selected_username,'selected_role': selected_role,})


# create/edit user
class create_edit_update_user(LoginRequiredMixin, View):
    login_url='/users/login/'
    template_name='dashboard/create_edit_user.html'

    def get_user(self, user_id):
        return user_service.get_user_by_id(user_id) if user_id else None
    
    def get(self, request, user_id=None):
        user=self.get_user(user_id)
        form=RegisterationForm(instance=user)

        return render(request, self.template_name, {
            'form': form,
            'editing_user':user
        })
    
    def post(self, request, user_id=None):
        user = self.get_user(user_id)
        form = RegisterationForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            new_user = form.save(commit=False)

            # Handle user creation
            if not user:
                password = request.POST.get("password")
                confirm = request.POST.get("confirmPassword")
                if password != confirm:
                    form.add_error("confirmPassword", "Passwords do not match")
                else:
                    new_user.set_password(password)

            # Handle user update and password change
            else:
                current = request.POST.get("current_password")
                new_pass = request.POST.get("new_password")
                confirm = request.POST.get("confirm_new_password")

                if new_pass:
                    if not user.check_password(current):
                        form.add_error("current_password", "Current password is incorrect")
                    elif new_pass != confirm:
                        form.add_error("confirm_new_password", "New passwords do not match")
                    else:
                        new_user.set_password(new_pass)

            # Handle image upload
            image = request.FILES.get("image")
            if image:
                user_service.handle_user_image_upload(new_user, image)

            if not form.errors:
                new_user.save()
                cache.delete('dashboard_counts')
                if user_id:
                    cache.delete(f"user:{user_id}")

                msg = "User created successfully" if not user else "User updated successfully"
                messages.success(request, msg)
                return redirect('/dashboard/users/')
        else:
            messages.error(request, "Please correct the errors")

        return render(request, self.template_name, {'form': form, 'editing_user': user})


# @login_required(login_url='/users/login/')
# def create_edit_update_user(request, user_id=None):
#     user=user_service.get_user_by_id(user_id) if user_id else None

#     if request.method == "POST":
#         form = RegisterationForm(request.POST, request.FILES, instance=user)

#         if form.is_valid():
#             new_user = form.save(commit=False)

#             # Handle creation
#             if not user:
#                 password = request.POST.get("password")
#                 confirm = request.POST.get("confirmPassword")

#                 if password != confirm:
#                     form.add_error("confirmPassword", "Passwords do not match")
#                 else:
#                     new_user.set_password(password)

#             else:
#                 current = request.POST.get("current_password")
#                 new_pass = request.POST.get("new_password")
#                 confirm = request.POST.get("confirm_new_password")

#                 if new_pass:
#                     if not user.check_password(current):
#                         form.add_error("current_password", "Current password is incorrect")
#                     elif new_pass != confirm:
#                         form.add_error("confirm_new_password", "New passwords do not match")
#                     else:
#                         new_user.set_password(new_pass)

#             image=request.FILES.get('image')

#             if image:
#                 user_service.handle_user_image_upload(new_user, image)

#             if not form.errors:
#                 new_user.save()
#                 cache.delete('dashboard_counts')

#                 if user_id:
#                     cache.delete(f"user:{user_id}")

#                 messages.success(request, "User created successfully" if not user else "User updated successfully")
#                 return redirect('/dashboard/users/')

#         else:
#             messages.error(request, "Please correct the errors")
#     else:
#         form = RegisterationForm(instance=user)

#     return render(request, 'dashboard/create_edit_user.html', {'form': form, 'editing_user': user})

# update own profile
class update_own_profile(LoginRequiredMixin, View):
    template_name='dashboard/create_edit_user.html'
    login_url='/users/login'

    def get_user(self, user_id):
        return user_service.get_user_by_id(user_id) if user_id else None
    
    def get(self, request, user_id=None):
        user = user_service.get_user_by_id(user_id)
        form = RegisterationForm(instance=user)
        form.fields['role'].required = False
        return render(request, self.template_name, {'form': form, 'editing_user': user})
    
    def post(self, request, user_id):
        user = user_service.get_user_by_id(user_id)
        form = RegisterationForm(request.POST, request.FILES, instance=user)
        form.fields['role'].required = False

        if form.is_valid():
            update_user = form.save(commit=False)

            # Handle password update
            current = request.POST.get("current_password")
            new_pass = request.POST.get("new_password")
            confirm = request.POST.get("confirm_new_password")

            if new_pass:
                if not user.check_password(current):
                    form.add_error("current_password", "Current password is incorrect")
                elif new_pass != confirm:
                    form.add_error("confirm_new_password", "New passwords do not match")
                else:
                    update_user.set_password(new_pass)

            # Handle image upload
            image = request.FILES.get("image")
            if image:
                user_service.handle_user_image_upload(user, image)

            if not form.errors:
                update_user.save()
                messages.success(request, "User updated successfully")
                return redirect('/dashboard/profile/')
        else:
            messages.warning(request, "Please enter valid data")

        return render(request, self.template_name, {'form': form, 'editing_user': user})


# @login_required(login_url='/users/login/')
# def update_own_profile(request, user_id):
#     user = user_service.get_user_by_id(user_id)

#     if request.method == 'POST':
#         form = RegisterationForm(request.POST, request.FILES, instance=user)
#         form.fields['role'].required = False
#         if form.is_valid():

#             update_user = form.save(commit=False)

#             # Handle password update
#             current = request.POST.get("current_password")
#             new_pass = request.POST.get("new_password")
#             confirm = request.POST.get("confirm_new_password")

#             if new_pass:
#                 if not user.check_password(current):
#                     form.add_error("current_password", "Current password is incorrect")
#                 elif new_pass != confirm:
#                     form.add_error("confirm_new_password", "New passwords do not match")
#                 else:
#                     update_user.set_password(new_pass)


#             # Handling images
#             image=request.FILES.get('image')

#             if image:
#                 user_service.handle_user_image_upload(user, image)


#             if not form.errors:
#                 update_user.save()
#                 messages.success(request, "User updated successfully")
#                 return redirect('/dashboard/profile/')
#         else:
#             print("Form errors:", form.errors) 
#             messages.warning(request, "Please enter valid data")

#     else:
#         form = RegisterationForm(instance=user)

#     return render(request, 'dashboard/create_edit_user.html', {
#         'form': form,
#         'editing_user': user
#     })



# delete user by id
class delete_user(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request, user_id):
        if request.user.role == 'manager':
            return redirect('/dashboard/home/')
        
        if request.user.role == 'employee':
            return redirect('/dashboard/tasks/')

        selected_page = request.GET.get('page', 1)
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully")
        cache.delete('dashboard_counts')
        return redirect(f'/dashboard/users/?page={selected_page}')



# @login_required(login_url='/users/login/')
# def delete_user(request, user_id):

#     if request.user.role == 'manager':
#         return redirect('/dashboard/home/')
    
#     if request.user.role == 'employee':
#         return redirect('/dashboard/tasks/')

#     selected_page = request.GET.get('page',1)
#     user = get_object_or_404(CustomUser, id=user_id)
#     user.delete()
#     messages.success(request, "User deleted successfully")
#     cache.delete('dashboard_counts')
#     return redirect(f'/dashboard/users/?page={selected_page}')


# logout
class logout_user(LoginRequiredMixin, View):
    def get(self, request):
        logout(self.request)
        return redirect('/users/login/')


# @login_required(login_url='/users/login/')
# def logout_user(request):
#     try:
#         logout(request)
#         return redirect('/users/login')
#     except:
#         messages.warning("Something went wrong")
        
                                                