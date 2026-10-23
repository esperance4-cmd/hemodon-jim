from django.urls import path
from . import views

app_name = 'centres'

urlpatterns = [
    # Carte interactive
    path('carte/', views.centres_map, name='map'),
    
    # Liste des centres
    path('centres/', views.centres_list, name='list'),
    
    # Détail d'un centre
    path('centres/<int:centre_id>/', views.centre_detail, name='detail'),
    
    # Recherche avancée
    path('rechercher/', views.centres_search, name='search'),
    
    # API (pour la carte)
    path('api/centres/', views.centres_api, name='api'),
]