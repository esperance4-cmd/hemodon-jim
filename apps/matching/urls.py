from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    # Dashboard
    path('matching/', views.matching_dashboard, name='dashboard'),
    
    # Suggestions pour une demande
    path('matching/suggestions/<int:demande_id>/', views.matching_suggestions, name='suggestions'),
    
    # Mettre à jour un match
    path('matching/update/<int:match_id>/', views.matching_update, name='update'),
    
    # Lancer le matching automatique
    path('matching/run/', views.matching_run, name='run'),
    
    # Recherche manuelle
    path('matching/search/', views.matching_search, name='search'),
    
    # Historique
    path('matching/historique/', views.matching_historique, name='historique'),
    
    # API
    path('matching/api/<int:demande_id>/', views.matching_api, name='api'),
]