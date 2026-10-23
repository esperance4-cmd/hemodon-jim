from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.authentification.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'groupe', 'telephone', 'est_eligible')
    list_filter = ('groupe', 'est_eligible', 'groupe_sanguin')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('groupe', 'telephone', 'adresse', 'commune', 'departement', 
                      'date_naissance', 'groupe_sanguin', 'est_eligible', 'photo')
        }),
    )

admin.site.register(User, CustomUserAdmin)