from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator

from .models import *
from .forms import *

@login_required
def mark_notifcation_read(request, notification_id):
    notification=get_object_or_404(Notifications, id=notification_id)
    notification.is_read=True
    notification.save()
    return redirect('dashboard/notifications.html/')

@login_required
def notification_list(request):
    if request.user.role in ['admin', 'manager']:
        notifications = Notifications.objects.all()
    else:
        notifications = Notifications.objects.filter(user=request.user)

    paginator = Paginator(notifications, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    pagecount = notifications.count()

    return render(request, 'dashboard/notifications.html', {
            'notifications': page,
            'page_obj': page,
            'notificationcount': pagecount,
        })

@login_required
def createNotification(request):
    if request.method == 'POST':
        form=BulkNotificationForm(request.post)

        if form.is_valid():
            message=form.cleaned_data['message']
            users=form.cleaned_data['send_to']

            for user in users:
                Notifications.objects.create(sender=request.user, user=user, message=message)
            
            
            messages.success("Message sent successfully")
            return redirect('/dashboard/notifications/')
        else:
            messages.warning("Please enter a valid data")
            return redirect('/dashboard/notifications/create/')
    
    else:
        form=BulkNotificationForm()

    return render(request, 'dashborad/create_notification.html',{
        'form':form
    })

@login_required
def deleteNotification(request, notification_id):
    if request.user.role == 'admin':
        notification=get_object_or_404(Notifications, id=notification_id)
        notification.delete()
        return redirect('/dashboard/notifications/')
    else:
        redirect('/dashboard/notifications/')

            
@login_required
def showNotification(request, notification_id):
    notification=get_object_or_404(Notifications, id=notification_id)

    return render(request, "dashboard/notification_detail.html", {
        'notification':notification
    })