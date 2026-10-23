from django.contrib import admin
from .models import Don

@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display = ('donneur', 'centre', 'date_planifiee', 'statut', 'quantite')
    list_filter = ('statut', 'centre', 'date_planifiee')
    search_fields = ('donneur__username', 'centre__nom')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations du don', {
            'fields': ('donneur', 'centre', 'quantite')
        }),
        ('Dates', {
            'fields': ('date_planifiee', 'date_effectuee')
        }),
        ('Statut', {
            'fields': ('statut', 'observations')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )