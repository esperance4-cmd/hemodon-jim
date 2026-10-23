from django.urls import path
from apps.app_admin import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.user_notifications, name='list'),
    path('notifications/<int:notif_id>/mark-read/', views.user_notification_mark_read, name='mark_read'),
    path('notifications/mark-all-read/', views.user_notification_mark_all_read, name='mark_all_read'),
    path('notifications/count/', views.user_notifications_count, name='count'),
    path('notifications/badge/', views.user_notifications_badge, name='badge'),
]