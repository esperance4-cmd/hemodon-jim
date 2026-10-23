from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('centre', 'groupe_sanguin', 'quantite_disponible', 'seuil_alerte', 'est_en_alerte')
    list_filter = ('centre', 'groupe_sanguin')
    search_fields = ('centre__nom',)
    readonly_fields = ('date_mise_a_jour',)