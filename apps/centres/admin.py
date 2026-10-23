from django.contrib import admin
from .models import Centre

@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'commune', 'departement', 'telephone', 'est_actif')
    list_filter = ('type', 'departement', 'est_actif')
    search_fields = ('nom', 'commune', 'adresse')