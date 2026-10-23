from django.contrib import admin
from .models import Notification, AuditLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type', 'est_lue', 'date_creation')
    list_filter = ('type', 'est_lue')
    search_fields = ('titre', 'message')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'action', 'modele', 'date_action')
    list_filter = ('action', 'modele')
    search_fields = ('utilisateur__username', 'modele', 'objet_repr')