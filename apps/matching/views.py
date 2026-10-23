from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count

from apps.demandes.models import Demande
from apps.authentification.models import User
from .models import MatchSuggestion, MatchingLog
from core.matching import (
    trouver_donneurs_compatibles,
    suggerer_donneurs_pour_demande,
    matching_automatique,
    calculer_score_compatibilite
)
from apps.app_admin.models import Notification


# ============================================
# DASHBOARD MATCHING
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_dashboard(request):
    """Dashboard du système de matching"""
    
    # Statistiques
    stats = {
        'total_matchs': MatchSuggestion.objects.count(),
        'en_attente': MatchSuggestion.objects.filter(statut='en_attente').count(),
        'acceptes': MatchSuggestion.objects.filter(statut='accepte').count(),
        'refuses': MatchSuggestion.objects.filter(statut='refuse').count(),
        'taux_succes': 0
    }
    
    if stats['total_matchs'] > 0:
        stats['taux_succes'] = round(
            (stats['acceptes'] / stats['total_matchs']) * 100, 1
        )
    
    # Derniers matchs
    derniers_matchs = MatchSuggestion.objects.select_related(
        'demande', 'donneur', 'centre'
    ).all().order_by('-date_suggestion')[:20]
    
    # Demandes en attente de matching
    demandes_en_attente = Demande.objects.filter(
        Q(urgence=True) | Q(statut__in=['en_attente', 'en_cours'])
    ).count()
    
    context = {
        'stats': stats,
        'derniers_matchs': derniers_matchs,
        'demandes_en_attente': demandes_en_attente,
        'title': 'Dashboard Matching - HEMODON-JIM',
        'active_page': 'matching',
    }
    return render(request, 'matching/dashboard.html', context)


# ============================================
# SUGGESTIONS POUR UNE DEMANDE
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_suggestions(request, demande_id):
    """Voir les suggestions pour une demande"""
    demande = get_object_or_404(Demande, id=demande_id)
    
    # Récupérer ou générer les suggestions
    suggestions = MatchSuggestion.objects.filter(demande=demande).select_related(
        'donneur', 'centre'
    ).order_by('-score')
    
    if not suggestions.exists():
        # Générer automatiquement
        suggestions = suggerer_donneurs_pour_demande(demande)
    
    context = {
        'demande': demande,
        'suggestions': suggestions,
        'title': f'Suggestions - Demande #{demande.id}',
        'active_page': 'matching',
    }
    return render(request, 'matching/suggestions.html', context)


# ============================================
# GÉRER UN MATCH
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_update(request, match_id):
    """Mettre à jour un match (accepter/refuser)"""
    match = get_object_or_404(MatchSuggestion, id=match_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accepter':
            match.accepter()
            
            # Créer une notification pour le donneur
            Notification.objects.create(
                titre=f"✅ Vous êtes compatible avec une demande urgente !",
                message=f"Votre profil correspond à une demande de sang de type {match.demande.groupe_sanguin}.",
                type='success',
                pour_tous=False,
                utilisateurs=[match.donneur],
                lien=f"/demandes/{match.demande.id}/"
            )
            
            messages.success(request, f"Match #{match.id} accepté avec succès.")
            
        elif action == 'refuser':
            match.refuser()
            messages.info(request, f"Match #{match.id} refusé.")
        
        elif action == 'notifier':
            match.notifier()
            
            # Notifier le donneur
            Notification.objects.create(
                titre=f"🩸 Nouveau besoin de sang !",
                message=f"Une demande de sang de type {match.demande.groupe_sanguin} a besoin de vous.",
                type='info',
                pour_tous=False,
                utilisateurs=[match.donneur],
                lien=f"/demandes/{match.demande.id}/"
            )
            
            messages.success(request, f"Donneur notifié avec succès.")
        
        return redirect('matching:suggestions', demande_id=match.demande.id)
    
    return redirect('matching:suggestions', demande_id=match.demande.id)


# ============================================
# MATCHING AUTOMATIQUE
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_run(request):
    """Lancer le matching automatique"""
    if request.method == 'POST':
        logs = matching_automatique()
        
        total_suggestions = sum(log.nb_suggestions for log in logs)
        
        messages.success(
            request,
            f"Matching automatique terminé : {len(logs)} demande(s) traitées, "
            f"{total_suggestions} suggestion(s) générées."
        )
        
        return redirect('matching:dashboard')
    
    return redirect('matching:dashboard')


# ============================================
# RECHERCHE MANUELLE DE DONNEURS
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_search(request):
    """Recherche manuelle de donneurs compatibles"""
    if request.method == 'POST':
        demande_id = request.POST.get('demande_id')
        max_resultats = int(request.POST.get('max_resultats', 10))
        
        demande = get_object_or_404(Demande, id=demande_id)
        
        # Trouver les donneurs compatibles
        resultats = trouver_donneurs_compatibles(demande, max_resultats)
        
        return render(request, 'matching/search_results.html', {
            'demande': demande,
            'resultats': resultats,
            'title': 'Résultats de recherche',
            'active_page': 'matching',
        })
    
    # GET : afficher le formulaire
    demandes_urgentes = Demande.objects.filter(
        Q(urgence=True) | Q(statut__in=['en_attente', 'en_cours'])
    )
    
    context = {
        'demandes_urgentes': demandes_urgentes,
        'title': 'Rechercher des donneurs',
        'active_page': 'matching',
    }
    return render(request, 'matching/search.html', context)


# ============================================
# HISTORIQUE DES MATCHS
# ============================================

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def matching_historique(request):
    """Historique des matchs"""
    matchs = MatchSuggestion.objects.select_related(
        'demande', 'donneur', 'centre'
    ).all().order_by('-date_suggestion')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        matchs = matchs.filter(statut=statut)
    
    paginator = Paginator(matchs, 30)
    page_number = request.GET.get('page')
    matchs_page = paginator.get_page(page_number)
    
    context = {
        'matchs': matchs_page,
        'statuts': MatchSuggestion.STATUT_CHOICES,
        'title': 'Historique des matchs',
        'active_page': 'matching',
    }
    return render(request, 'matching/historique.html', context)


# ============================================
# API - RECUPERER LES SUGGESTIONS
# ============================================

@login_required
def matching_api(request, demande_id):
    """API pour récupérer les suggestions (JSON)"""
    demande = get_object_or_404(Demande, id=demande_id)
    
    suggestions = MatchSuggestion.objects.filter(demande=demande).select_related(
        'donneur', 'centre'
    ).order_by('-score')
    
    data = []
    for match in suggestions:
        data.append({
            'id': match.id,
            'donneur': match.donneur.username,
            'donneur_id': match.donneur.id,
            'centre': match.centre.nom,
            'score': match.score,
            'distance_km': match.distance_km,
            'statut': match.statut,
            'statut_label': match.get_statut_display(),
            'date': match.date_suggestion.strftime('%d/%m/%Y %H:%M'),
        })
    
    return JsonResponse({
        'demande_id': demande.id,
        'groupe_sanguin': demande.groupe_sanguin,
        'suggestions': data
    }, safe=False)