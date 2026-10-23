from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.db import models

from .models import Demande
from apps.centres.models import Centre
from apps.stocks.models import Stock
from .forms import DemandeCreateForm, DemandeUpdateForm, DemandeFilterForm
from apps.app_admin.models import AuditLog


@login_required
def demandes_list(request):
    """Liste des demandes de l'utilisateur"""
    # Récupérer les demandes de l'utilisateur
    demandes = Demande.objects.filter(demandeur=request.user).order_by('-date_demande')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    urgence = request.GET.get('urgence')
    if urgence == 'true':
        demandes = demandes.filter(urgence=True)
    
    search = request.GET.get('search')
    if search:
        demandes = demandes.filter(
            Q(id__icontains=search) |
            Q(centre_destination__nom__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(demandes, 10)
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Demande.objects.filter(demandeur=request.user).count(),
        'en_attente': Demande.objects.filter(demandeur=request.user, statut='en_attente').count(),
        'traitees': Demande.objects.filter(demandeur=request.user, statut='traitee').count(),
        'urgentes': Demande.objects.filter(demandeur=request.user, urgence=True).count(),
    }
    
    context = {
        'demandes': demandes_page,
        'stats': stats,
        'statuts': Demande.STATUT_CHOICES,
        'title': 'Mes demandes - HEMODON-JIM',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/list.html', context)


@login_required
def demande_create(request):
    """Créer une demande de sang"""
    if request.method == 'POST':
        form = DemandeCreateForm(request.POST, user=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            
            # Vérifier les stocks disponibles
            stock = Stock.objects.filter(
                centre=demande.centre_destination,
                groupe_sanguin=demande.groupe_sanguin
            ).first()
            
            if stock and stock.quantite_disponible >= demande.quantite_necessaire:
                demande.statut = 'traitee'
                demande.date_traitement = timezone.now()
                demande.save()
                stock.quantite_disponible -= demande.quantite_necessaire
                stock.save()
                messages.success(request, "Demande traitée automatiquement ! Stock disponible.")
            else:
                messages.info(request, "Demande enregistrée en attente de traitement.")
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='create',
                modele='Demande',
                objet_id=demande.id,
                objet_repr=f"Demande #{demande.id}",
                details={
                    'groupe': demande.groupe_sanguin,
                    'quantite': demande.quantite_necessaire,
                    'urgence': demande.urgence
                }
            )
            
            return redirect('demandes:list')
    else:
        form = DemandeCreateForm(user=request.user)
    
    context = {
        'form': form,
        'centres': Centre.objects.filter(est_actif=True),
        'title': 'Faire une demande de sang - HEMODON-JIM',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/create.html', context)


@login_required
def demande_detail(request, demande_id):
    """Détail d'une demande"""
    demande = get_object_or_404(Demande, id=demande_id, demandeur=request.user)
    
    # Vérifier les stocks disponibles
    stock = Stock.objects.filter(
        centre=demande.centre_destination,
        groupe_sanguin=demande.groupe_sanguin
    ).first()
    
    stock_disponible = stock.quantite_disponible if stock else 0
    peut_traiter = demande.statut in ['en_attente', 'en_cours'] and stock_disponible >= demande.quantite_necessaire
    
    context = {
        'demande': demande,
        'stock_disponible': stock_disponible,
        'peut_traiter': peut_traiter,
        'title': f'Demande #{demande.id} - HEMODON-JIM',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/detail.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts', 'hospitalier'])
def demande_update(request, demande_id):
    """Traiter une demande (admin seulement)"""
    demande = get_object_or_404(Demande, id=demande_id)
    
    if request.method == 'POST':
        form = DemandeUpdateForm(request.POST, instance=demande)
        if form.is_valid():
            ancien_statut = demande.statut
            demande = form.save(commit=False)
            
            # Si la demande est traitée, déduire des stocks
            if demande.statut == 'traitee' and ancien_statut != 'traitee':
                stock = Stock.objects.filter(
                    centre=demande.centre_destination,
                    groupe_sanguin=demande.groupe_sanguin
                ).first()
                
                if stock and stock.quantite_disponible >= demande.quantite_necessaire:
                    stock.quantite_disponible -= demande.quantite_necessaire
                    stock.save()
                    demande.date_traitement = timezone.now()
                    messages.success(request, f"Demande #{demande.id} traitée avec succès.")
                else:
                    messages.error(request, "Stock insuffisant pour traiter cette demande.")
                    demande.statut = ancien_statut
                    form.add_error(None, "Stock insuffisant.")
                    return render(request, 'demandes/update.html', {
                        'form': form,
                        'demande': demande,
                        'title': f'Traiter la demande #{demande.id}',
                        'active_page': 'demandes',
                    })
            
            demande.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Demande',
                objet_id=demande.id,
                objet_repr=f"Demande #{demande.id}",
                details={'statut': demande.statut, 'urgence': demande.urgence}
            )
            
            messages.success(request, f"Demande #{demande.id} mise à jour avec succès.")
            return redirect('demandes:list')
    else:
        form = DemandeUpdateForm(instance=demande)
    
    context = {
        'form': form,
        'demande': demande,
        'statuts': Demande.STATUT_CHOICES,
        'title': f'Traiter la demande #{demande.id}',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/update.html', context)


@login_required
def demande_annuler(request, demande_id):
    """Annuler une demande (admin seulement)"""
    demande = get_object_or_404(Demande, id=demande_id)
    
    if request.user != demande.demandeur and request.user.groupe not in ['admin', 'pnts']:
        messages.error(request, "Vous n'avez pas les droits pour annuler cette demande.")
        return redirect('demandes:list')
    
    if request.method == 'POST':
        if demande.statut in ['traitee', 'annulee']:
            messages.error(request, "Cette demande ne peut pas être annulée.")
        else:
            # Si la demande a été traitée, remettre les stocks
            if demande.statut == 'traitee':
                stock = Stock.objects.filter(
                    centre=demande.centre_destination,
                    groupe_sanguin=demande.groupe_sanguin
                ).first()
                if stock:
                    stock.quantite_disponible += demande.quantite_necessaire
                    stock.save()
            
            demande.statut = 'annulee'
            demande.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Demande',
                objet_id=demande.id,
                objet_repr=f"Demande #{demande.id}",
                details={'statut': 'annulee'}
            )
            
            messages.success(request, f"Demande #{demande.id} annulée avec succès.")
        return redirect('demandes:list')
    
    context = {
        'demande': demande,
        'title': f'Annuler la demande #{demande.id}',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/confirm_delete.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def demandes_toutes(request):
    """Toutes les demandes (admin)"""
    demandes = Demande.objects.select_related('demandeur', 'centre_destination').all().order_by('-date_demande')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    urgence = request.GET.get('urgence')
    if urgence == 'true':
        demandes = demandes.filter(urgence=True)
    
    groupe = request.GET.get('groupe_sanguin')
    if groupe:
        demandes = demandes.filter(groupe_sanguin=groupe)
    
    search = request.GET.get('search')
    if search:
        demandes = demandes.filter(
            Q(id__icontains=search) |
            Q(demandeur__username__icontains=search) |
            Q(centre_destination__nom__icontains=search)
        )
    
    paginator = Paginator(demandes, 20)
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    context = {
        'demandes': demandes_page,
        'statuts': Demande.STATUT_CHOICES,
        'groupes': Demande.GROUPE_CHOICES,
        'title': 'Toutes les demandes - HEMODON-JIM',
        'active_page': 'demandes',
    }
    return render(request, 'demandes/toutes.html', context)


def demandes_api(request):
    """API pour récupérer les demandes (format JSON)"""
    demandes = Demande.objects.select_related('demandeur', 'centre_destination').all()
    
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    data = []
    for demande in demandes:
        data.append({
            'id': demande.id,
            'demandeur': demande.demandeur.username,
            'groupe_sanguin': demande.groupe_sanguin,
            'quantite': demande.quantite_necessaire,
            'statut': demande.statut,
            'statut_label': demande.get_statut_display(),
            'urgence': demande.urgence,
            'centre': demande.centre_destination.nom,
            'date': demande.date_demande.strftime('%d/%m/%Y %H:%M'),
        })
    
    return JsonResponse(data, safe=False)