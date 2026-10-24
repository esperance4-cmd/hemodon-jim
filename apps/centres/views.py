from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Centre
from apps.stocks.models import Stock


def centres_map(request):
    """Carte interactive des centres de transfusion"""
    centres = Centre.objects.filter(est_actif=True)
    
    # Préparer les données pour la carte (format GeoJSON simplifié)
    centres_data = []
    for centre in centres:
        if centre.latitude and centre.longitude:
            # Récupérer les stocks du centre
            stocks = Stock.objects.filter(centre=centre)
            stocks_data = {stock.groupe_sanguin: stock.quantite_disponible for stock in stocks}
            
            centres_data.append({
                'id': centre.id,
                'nom': centre.nom,
                'type': centre.type,
                'adresse': centre.adresse,
                'commune': centre.commune,
                'departement': centre.departement,
                'telephone': centre.telephone,
                'email': centre.email,
                'latitude': float(centre.latitude),
                'longitude': float(centre.longitude),
                'horaires': centre.horaires,
                'stocks': stocks_data,
                'capacite_journaliere': centre.capacite_journaliere,
            })
    
    context = {
        'centres': centres,
        'centres_json': json.dumps(centres_data),
        'title': 'Carte des centres - HEMODON-JIM',
        'active_page': 'centres',
    }
    return render(request, 'centres/map.html', context)


def centres_list(request):
    """Liste des centres de transfusion"""
    centres = Centre.objects.filter(est_actif=True).order_by('nom')
    
    # Filtres
    departement = request.GET.get('departement')
    if departement:
        centres = centres.filter(departement=departement)
    
    type_centre = request.GET.get('type')
    if type_centre:
        centres = centres.filter(type=type_centre)
    
    search = request.GET.get('search')
    if search:
        centres = centres.filter(
            Q(nom__icontains=search) |
            Q(commune__icontains=search) |
            Q(departement__icontains=search) |
            Q(adresse__icontains=search)
        )
    
    paginator = Paginator(centres, 12)
    page_number = request.GET.get('page')
    centres_page = paginator.get_page(page_number)
    
    # Récupérer les départements pour le filtre
    departements = Centre.objects.filter(est_actif=True).values_list('departement', flat=True).distinct()
    
    context = {
        'centres': centres_page,
        'departements': sorted(departements),
        'types': Centre.TYPE_CHOICES,
        'title': 'Liste des centres - HEMODON-JIM',
        'active_page': 'centres',
    }
    return render(request, 'centres/list.html', context)


def centre_detail(request, centre_id):
    """Détail d'un centre de transfusion"""
    centre = get_object_or_404(Centre, id=centre_id, est_actif=True)
    stocks = Stock.objects.filter(centre=centre)
    
    # Vérifier si le centre a des stocks critiques
    stocks_critiques = stocks.filter(quantite_disponible__lte=F('seuil_alerte'))
    
    context = {
        'centre': centre,
        'stocks': stocks,
        'stocks_critiques': stocks_critiques,
        'title': f'{centre.nom} - HEMODON-JIM',
        'active_page': 'centres',
    }
    return render(request, 'centres/detail.html', context)


@login_required
def centres_search(request):
    """Recherche avancée de centres"""
    centres = Centre.objects.filter(est_actif=True)
    
    # Recherche par mot-clé
    query = request.GET.get('q')
    if query:
        centres = centres.filter(
            Q(nom__icontains=query) |
            Q(commune__icontains=query) |
            Q(departement__icontains=query)
        )
    
    # Filtres
    groupe_sanguin = request.GET.get('groupe_sanguin')
    if groupe_sanguin:
        centres = centres.filter(stocks__groupe_sanguin=groupe_sanguin, stocks__quantite_disponible__gt=0)
    
    departement = request.GET.get('departement')
    if departement:
        centres = centres.filter(departement=departement)
    
    # Pagination
    paginator = Paginator(centres, 12)
    page_number = request.GET.get('page')
    centres_page = paginator.get_page(page_number)
    
    departements = Centre.objects.filter(est_actif=True).values_list('departement', flat=True).distinct()
    
    context = {
        'centres': centres_page,
        'query': query,
        'departements': sorted(departements),
        'groupes_sanguins': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'title': 'Rechercher un centre - HEMODON-JIM',
        'active_page': 'centres',
    }
    return render(request, 'centres/search.html', context)


@require_http_methods(["GET"])
def centres_api(request):
    """API pour récupérer les centres (format GeoJSON)"""
    centres = Centre.objects.filter(est_actif=True)
    
    features = []
    for centre in centres:
        if centre.latitude and centre.longitude:
            stocks = Stock.objects.filter(centre=centre)
            stocks_data = {stock.groupe_sanguin: stock.quantite_disponible for stock in stocks}
            
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(centre.longitude), float(centre.latitude)]
                },
                'properties': {
                    'id': centre.id,
                    'nom': centre.nom,
                    'type': centre.type,
                    'adresse': centre.adresse,
                    'commune': centre.commune,
                    'departement': centre.departement,
                    'telephone': centre.telephone,
                    'email': centre.email,
                    'horaires': centre.horaires,
                    'stocks': stocks_data,
                }
            })
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return JsonResponse(geojson)