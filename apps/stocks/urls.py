from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    # Liste globale des stocks
    path('stocks/', views.stocks_list, name='list'),
    
    # Stocks d'un centre spécifique
    path('stocks/centre/<int:centre_id>/', views.stocks_centre, name='centre'),
    
    # Mettre à jour un stock (admin)
    path('stocks/<int:stock_id>/update/', views.stock_update, name='update'),
    
    # Mise à jour groupée (admin)
    path('stocks/bulk-update/', views.stock_bulk_update, name='bulk_update'),
    
    # Alertes stocks critiques
    path('stocks/alertes/', views.stocks_alertes, name='alertes'),
    
    # API
    path('api/stocks/', views.stocks_api, name='api'),
]