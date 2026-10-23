from django.urls import path
from . import views

app_name = 'demandes'

urlpatterns = [
    # Liste des demandes de l'utilisateur
    path('mes-demandes/', views.demandes_list, name='list'),
    
    # Créer une demande
    path('demandes/creer/', views.demande_create, name='create'),
    
    # Détail d'une demande
    path('demandes/<int:demande_id>/', views.demande_detail, name='detail'),
    
    # Traiter une demande (admin)
    path('demandes/<int:demande_id>/traiter/', views.demande_update, name='update'),
    
    # Annuler une demande (admin)
    path('demandes/<int:demande_id>/annuler/', views.demande_annuler, name='annuler'),
    
    # Toutes les demandes (admin)
    path('demandes/toutes/', views.demandes_toutes, name='toutes'),
    
    # API
    path('api/demandes/', views.demandes_api, name='api'),
]