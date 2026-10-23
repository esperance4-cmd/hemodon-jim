from django.db import models
from apps.app_admin.models import Notification


def user_notifications_count(request):
    """Context processor pour le compteur de notifications"""
    count = 0
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            models.Q(pour_tous=True) | models.Q(utilisateurs=request.user),
            est_lue=False
        ).distinct().count()
        print(f"Notifications non lues pour {request.user.username}: {count}")
    return {'user_notifications_count': count}