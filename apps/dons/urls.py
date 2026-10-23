from django.urls import path
from . import views

app_name = 'dons'

urlpatterns = [
    # Liste des dons
    path('mes-dons/', views.dons_list, name='my_dons'),
    
    # Créer un don
    path('dons/creer/', views.don_create, name='create'),
    
    # Détail d'un don
    path('dons/<int:don_id>/', views.don_detail, name='detail'),
    
    # Annuler un don
    path('dons/<int:don_id>/annuler/', views.don_annuler, name='annuler'),
    
    # Modifier un don (admin)
    path('dons/<int:don_id>/modifier/', views.don_update, name='update'),
]