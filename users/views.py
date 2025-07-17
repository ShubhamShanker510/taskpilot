from django.shortcuts import render,redirect, get_object_or_404, get_list_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from .models import *
from .forms import *
from tasks.models import *
from projects.models import *

@login_required(login_url='/users/login/')
def home(request):

    if hasattr(request.user, 'role') and request.user.role == 'employee':
        return redirect('/dashboard/tasks/')

    pending_task=Task.objects.filter(status="pending").count()
    completed_task=Task.objects.filter(status="done").count()
    inprogress_task=Task.objects.filter(status="in_progress").count()
    total_admin=CustomUser.objects.filter(role="admin").count()
    total_manager=CustomUser.objects.filter(role="manager").count()
    total_employee=CustomUser.objects.filter(role="employee").count()
    total_projects=Project.objects.all().count()

    return render(request, 'dashboard/home.html',{
        'pending_task':pending_task,
        'completed_task':completed_task,
        'inprogress_task':inprogress_task,
        'total_admin':total_admin,
        'total_manager':total_manager,
        'total_employee':total_employee,
        'total_projects':total_projects
    })


# custom redirect to login
def redirect_to_login(request):
    return redirect('/users/login')

#login form
def login_user(request):
    if request.method=="POST":
        form=LoginForm(request.POST)

        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']

            user=authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request,"User Login successfully")
                
                if request.user.role == 'admin' or request.user.role == 'manager':
                    return redirect('/dashboard/home/')
                elif request.user.role == 'employee':
                    return redirect('/dashboard/tasks')
            
            else:
                messages.error(request, "Invalid user")
        else:
            messages.error(request, "Please enter valid data")
    
    else:
        form=LoginForm()
    
    return render(request, "users/login.html", {'form':form})


# user profile
@login_required(login_url='/users/login/')
def user_profile(request):
    user=request.user

    return render(request, 'dashboard/user_profile.html', {'user':user})

# user_table
@login_required(login_url='/users/login/')
def user_table(request):
    if request.user.role == 'manager':
        return redirect('/dashboard/home/')
    
    if request.user.role == 'employee':
        return redirect('/dashboard/tasks/')

    users=CustomUser.objects.filter(is_superuser = False)

    # filter-searching
    selected_username=request.GET.get('username', '').strip()
    selected_role=request.GET.get('role','').strip()

    if selected_username:
        users=CustomUser.objects.filter(username__icontains=selected_username)
    elif selected_role:
        users=CustomUser.objects.filter(role=selected_role, is_superuser=False)

    users=users.order_by("id")
  
    paginator=Paginator(users, 5)
    page_number=request.GET.get('page')
    page=paginator.get_page(page_number)
    usercount=users.count()


    return render(request, 'dashboard/user_table.html', {'users': page,'page_obj':page,'usercount':usercount, 'selected_username': selected_username,'selected_role': selected_role,})


# create/edit user
@login_required(login_url='/users/login/')
def create_edit_update_user(request, user_id=None):
    user = get_object_or_404(CustomUser, id=user_id) if user_id else None

    if request.method == "POST":
        form = RegisterationForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            new_user = form.save(commit=False)

            # Handle creation
            if not user:
                password = request.POST.get("password")
                confirm = request.POST.get("confirmPassword")

                if password != confirm:
                    form.add_error("confirmPassword", "Passwords do not match")
                else:
                    new_user.set_password(password)

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

            # Handle image upload manually
            if 'image' in request.FILES:
                new_user.image = request.FILES['image']

            if not form.errors:
                new_user.save()
                messages.success(request, "User created successfully" if not user else "User updated successfully")
                return redirect('/dashboard/users/')

        else:
            messages.error(request, "Please correct the errors")
    else:
        form = RegisterationForm(instance=user)

    return render(request, 'dashboard/create_edit_user.html', {'form': form, 'editing_user': user})

# update own profile
@login_required(login_url='/users/login/')
def update_own_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
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
            if 'image' in request.FILES:
                update_user.image = request.FILES['image']

            if not form.errors:
                update_user.save()
                messages.success(request, "User updated successfully")
                return redirect('/dashboard/profile/')
        else:
            print("Form errors:", form.errors) 
            messages.warning(request, "Please enter valid data")

    else:
        form = RegisterationForm(instance=user)

    return render(request, 'dashboard/create_edit_user.html', {
        'form': form,
        'editing_user': user
    })



# delete user by id
@login_required(login_url='/users/login/')
def delete_user(request, user_id):

    if request.user.role == 'manager':
        return redirect('/dashboard/home/')
    
    if request.user.role == 'employee':
        return redirect('/dashboard/tasks/')

    selected_page = request.GET.get('page',1)
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect(f'/dashboard/users/?page={selected_page}')


# logout
@login_required(login_url='/users/login/')
def logout_user(request):
    try:
        logout(request)
        return redirect('/users/login')
    except:
        messages.warning("Something went wrong")
        


        if hasattr(request.user, 'role') and request.user.role == 'employee':
            return redirect('/dashboard/tasks/')
        elif hasattr(request.user, 'role') and (request.user.role == 'manager' or request.user.role == 'admin'):
            return redirect('/dashboard/tasks')
                                                