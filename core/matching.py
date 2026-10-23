import math
from decimal import Decimal
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from haversine import haversine
from apps.authentification.models import User
from apps.centres.models import Centre
from apps.stocks.models import Stock
from apps.dons.models import Don
from apps.demandes.models import Demande
from .geo import distance as haversine
from .compatibilite import groupes_compatibles_pour_receveur


def calculer_score_compatibilite(donneur, demande, centre=None):
    """
    Calcule un score de compatibilité entre un donneur et une demande.
    
    Critères :
    - Groupe sanguin compatible (poids: 30%)
    - Distance (poids: 25%)
    - Historique des dons (poids: 20%)
    - Éligibilité (poids: 15%)
    - Proximité du dernier don (poids: 10%)
    
    Returns:
        int: Score de 0 à 100
    """
    score = 0
    
    # 1. Groupe sanguin (30%)
    groupes_compatibles = groupes_compatibles_pour_receveur(demande.groupe_sanguin)
    if donneur.groupe_sanguin in groupes_compatibles:
        score += 30
    else:
        return 0  # Incompatible, score nul
    
    # 2. Distance (25%)
    if centre and centre.latitude and centre.longitude and donneur.adresse:
        # Si le donneur n'a pas de coordonnées, on utilise le centre le plus proche
        distance = 100  # Valeur par défaut (100 km)
        # Dans la vraie vie, on utiliserait la géolocalisation du donneur
        # Pour l'instant, on simule une distance raisonnable
        score += 25 * max(0, 1 - (distance / 50))
    else:
        score += 15  # Distance inconnue, on donne un score moyen
    
    # 3. Historique des dons (20%)
    nb_dons = Don.objects.filter(donneur=donneur, statut='effectue').count()
    if nb_dons >= 5:
        score += 20
    elif nb_dons >= 3:
        score += 15
    elif nb_dons >= 1:
        score += 10
    else:
        score += 5
    
    # 4. Éligibilité (15%)
    if donneur.est_eligible:
        score += 15
    else:
        score += 0
    
    # 5. Proximité du dernier don (10%)
    dernier_don = Don.objects.filter(
        donneur=donneur,
        statut='effectue'
    ).order_by('-date_effectuee').first()
    
    if dernier_don:
        jours_depuis = (timezone.now() - dernier_don.date_effectuee).days
        if jours_depuis >= 90:  # 3 mois
            score += 10
        elif jours_depuis >= 60:
            score += 5
        else:
            score += 0
    else:
        score += 10  # Jamais donné, disponible immédiatement
    
    return min(score, 100)  # Ne pas dépasser 100


def trouver_donneurs_compatibles(demande, max_resultats=10, distance_max=50):
    """
    Trouve les donneurs les plus compatibles pour une demande.
    
    Args:
        demande: Objet Demande
        max_resultats: Nombre maximum de résultats
        distance_max: Distance maximale en km
    
    Returns:
        list: Liste de dict avec donneur, centre, score, distance
    """
    # 1. Groupes sanguins compatibles
    groupes_compatibles = groupes_compatibles_pour_receveur(demande.groupe_sanguin)
    
    # 2. Donneurs éligibles
    date_limite = timezone.now() - timedelta(days=90)
    
    donneurs = User.objects.filter(
        groupe='donneur',
        est_eligible=True,
        is_active=True,
        groupe_sanguin__in=groupes_compatibles
    ).exclude(
        # Exclure ceux qui ont donné récemment (moins de 3 mois)
        dons__date_effectuee__gte=date_limite,
        dons__statut='effectue'
    ).distinct()
    
    # 3. Trouver les centres proches
    centres_proches = Centre.objects.filter(
        est_actif=True
    )
    
    if demande.centre_destination.latitude and demande.centre_destination.longitude:
        # Filtrer les centres dans un rayon
        # (Dans la vraie vie, on utiliserait une requête spatiale)
        pass
    
    # 4. Calculer les scores
    resultats = []
    lat_demande = float(demande.centre_destination.latitude or 0)
    lon_demande = float(demande.centre_destination.longitude or 0)
    
    for donneur in donneurs:
        # Trouver le centre le plus proche du donneur
        centre_plus_proche = None
        distance_min = float('inf')
        
        for centre in centres_proches:
            if centre.latitude and centre.longitude:
                distance = haversine(
                    lat_demande,
                    lon_demande,
                    float(centre.latitude),
                    float(centre.longitude)
                )
                if distance < distance_min:
                    distance_min = distance
                    centre_plus_proche = centre
        
        if distance_min <= distance_max:
            score = calculer_score_compatibilite(
                donneur,
                demande,
                centre_plus_proche
            )
            
            if score > 0:
                resultats.append({
                    'donneur': donneur,
                    'centre': centre_plus_proche,
                    'score': score,
                    'distance_km': round(distance_min, 2)
                })
    
    # 5. Trier par score décroissant
    resultats.sort(key=lambda x: x['score'], reverse=True)
    
    return resultats[:max_resultats]


def suggerer_donneurs_pour_demande(demande, max_resultats=10):
    """
    Génère des suggestions de donneurs pour une demande.
    """
    from apps.matching.models import MatchSuggestion
    
    # Trouver les donneurs compatibles
    donneurs_trouves = trouver_donneurs_compatibles(demande, max_resultats)
    
    suggestions = []
    for data in donneurs_trouves:
        # Vérifier si un match existe déjà
        match, created = MatchSuggestion.objects.get_or_create(
            demande=demande,
            donneur=data['donneur'],
            defaults={
                'centre': data['centre'],
                'score': data['score'],
                'distance_km': data['distance_km'],
                'statut': 'en_attente'
            }
        )
        suggestions.append(match)
    
    return suggestions


def trouver_centres_avec_stock(groupe_sanguin, quantite_min=1):
    """
    Trouve les centres qui ont du stock disponible.
    """
    stocks = Stock.objects.filter(
        groupe_sanguin=groupe_sanguin,
        quantite_disponible__gte=quantite_min
    ).select_related('centre')
    
    return [stock.centre for stock in stocks if stock.centre.est_actif]


def matching_automatique(demande_id=None):
    """
    Lancement automatique du matching pour toutes les demandes urgentes.
    """
    from apps.matching.models import MatchSuggestion, MatchingLog
    from apps.app_admin.models import Notification
    
    # Récupérer les demandes urgentes ou en attente
    if demande_id:
        demandes = Demande.objects.filter(id=demande_id)
    else:
        demandes = Demande.objects.filter(
            Q(urgence=True) | Q(statut__in=['en_attente', 'en_cours'])
        )
    
    logs = []
    
    for demande in demandes:
        # Générer les suggestions
        suggestions = suggerer_donneurs_pour_demande(demande, max_resultats=10)
        
        # Créer un log
        log = MatchingLog.objects.create(
            demande=demande,
            action='auto',
            nb_suggestions=len(suggestions),
            details={
                'groupes_compatibles': groupes_compatibles_pour_receveur(demande.groupe_sanguin),
                'nb_suggestions': len(suggestions)
            }
        )
        logs.append(log)
        
        # Créer des notifications pour les matchs
        if suggestions:
            # Notifier les administrateurs
            admin_users = User.objects.filter(
                Q(is_superuser=True) | Q(groupe='admin') | Q(groupe='pnts')
            )
            
            for admin in admin_users:
                Notification.objects.create(
                    titre=f"🔔 Nouveau match pour la demande #{demande.id}",
                    message=f"{len(suggestions)} donneur(s) compatible(s) trouvé(s) pour la demande de {demande.groupe_sanguin}.",
                    type='success',
                    pour_tous=False,
                    utilisateurs=[admin],
                    lien=f"/admin-panel/demandes/{demande.id}/"
                )
    
    return logs