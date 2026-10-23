from django.contrib import admin
from .models import Demande

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'groupe_sanguin', 'statut', 'urgence', 'quantite_necessaire', 'date_demande')
    list_filter = ('statut', 'urgence', 'groupe_sanguin')
    search_fields = ('demandeur__username', 'centre_destination__nom')
    readonly_fields = ('date_demande', 'created_at', 'updated_at')