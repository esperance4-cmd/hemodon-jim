from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    """Liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(
        user=request.user,
        type='in_app'
    )
    
    unread_count = notifications.filter(status='pending').count()
    
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_as_read(request, notification_id):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'success': True})


@login_required
def mark_all_read(request):
    """Marquer toutes les notifications comme lues"""
    Notification.objects.filter(user=request.user, status='pending').update(
        status='read',
        read_at=timezone.now()
    )
    return JsonResponse({'success': True})


@login_required
def unread_count(request):
    """Obtenir le nombre de notifications non lues"""
    count = Notification.objects.filter(
        user=request.user,
        status='pending'
    ).count()
    return JsonResponse({'unread_count': count})