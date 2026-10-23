from django.urls import path
from . import views

app_name = 'app_admin'

urlpatterns = [
    # Tableau de bord
    path('admin-panel/', views.admin_dashboard, name='dashboard'),
    
    # Utilisateurs
    path('admin-panel/users/', views.admin_users, name='users'),
    path('admin-panel/users/<int:user_id>/', views.admin_user_detail, name='user_detail'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('admin-panel/users/<int:user_id>/toggle/', views.admin_user_toggle, name='user_toggle'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),

    # Notifications (admin)
    path('admin-panel/notifications/', views.admin_notifications, name='notifications'),
    path('admin-panel/notifications/create/', views.admin_notification_create, name='notification_create'),
    path('admin-panel/notifications/<int:notif_id>/delete/', views.admin_notification_delete, name='notification_delete'),
    path('admin-panel/notifications/<int:notif_id>/toggle-read/', views.admin_notification_toggle_read, name='notification_toggle_read'),
    
    # Centres
    path('admin-panel/centres/', views.admin_centres, name='centres'),
    path('admin-panel/centres/create/', views.admin_centre_create, name='centre_create'),
    path('admin-panel/centres/<int:centre_id>/edit/', views.admin_centre_edit, name='centre_edit'),
    path('admin-panel/centres/<int:centre_id>/delete/', views.admin_centre_delete, name='centre_delete'),
    
    # Stocks
    path('admin-panel/stocks/', views.admin_stocks, name='stocks'),
    path('admin-panel/stocks/<int:stock_id>/update/', views.admin_stock_update, name='stock_update'),
    
    # Demandes
    path('admin-panel/demandes/', views.admin_demandes, name='demandes'),
    path('admin-panel/demandes/<int:demande_id>/update/', views.admin_demande_update, name='demande_update'),
    
    # Notifications
    path('admin-panel/notifications/', views.admin_notifications, name='notifications'),
    path('admin-panel/notifications/create/', views.admin_notification_create, name='notification_create'),
    path('admin-panel/notifications/<int:notif_id>/delete/', views.admin_notification_delete, name='notification_delete'),
    path('admin-panel/notifications/<int:notif_id>/toggle-read/', views.admin_notification_toggle_read, name='notification_toggle_read'),
    
    # Logs
    path('admin-panel/logs/', views.admin_logs, name='logs'),
    
    # Rapports
    path('admin-panel/reports/', views.admin_reports, name='reports'),
    
    # Export
    path('admin-panel/export/<str:modele>/', views.admin_export, name='export'),
]