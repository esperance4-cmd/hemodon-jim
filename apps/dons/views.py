from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Don
from apps.centres.models import Centre
from .forms import DonCreateForm, DonUpdateForm
from apps.app_admin.models import AuditLog


@login_required
def dons_list(request):
    """Liste des dons de l'utilisateur"""
    # Récupérer les dons de l'utilisateur
    dons = Don.objects.filter(donneur=request.user).order_by('-date_planifiee')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        dons = dons.filter(statut=statut)
    
    # Pagination
    paginator = Paginator(dons, 10)
    page_number = request.GET.get('page')
    dons_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Don.objects.filter(donneur=request.user).count(),
        'effectues': Don.objects.filter(donneur=request.user, statut='effectue').count(),
        'planifies': Don.objects.filter(donneur=request.user, statut='planifie').count(),
        'annules': Don.objects.filter(donneur=request.user, statut='annule').count(),
    }
    
    context = {
        'dons': dons_page,
        'stats': stats,
        'statuts': Don.STATUT_CHOICES,
        'title': 'Mes dons - HEMODON-JIM',
        'active_page': 'dons',
    }
    return render(request, 'dons/list.html', context)


@login_required
def don_create(request):
    """Planifier un don"""
    if request.method == 'POST':
        form = DonCreateForm(request.POST)
        if form.is_valid():
            don = form.save(commit=False)
            don.donneur = request.user
            don.save()
            
            # Journaliser l'action
            AuditLog.objects.create(
                utilisateur=request.user,
                action='create',
                modele='Don',
                objet_id=don.id,
                objet_repr=f"Don #{don.id}",
                details={'centre': don.centre.nom, 'date': str(don.date_planifiee)}
            )
            
            messages.success(
                request, 
                f"Votre don au {don.centre.nom} a été planifié avec succès pour le {don.date_planifiee.strftime('%d/%m/%Y à %H:%M')} !"
            )
            return redirect('dons:my_dons')
    else:
        form = DonCreateForm()
    
    context = {
        'form': form,
        'title': 'Planifier un don - HEMODON-JIM',
        'active_page': 'dons',
    }
    return render(request, 'dons/create.html', context)


@login_required
def don_detail(request, don_id):
    """Détail d'un don"""
    don = get_object_or_404(Don, id=don_id, donneur=request.user)
    
    # Vérifier si le don peut être annulé
    peut_annuler = don.peut_annuler()
    
    context = {
        'don': don,
        'peut_annuler': peut_annuler,
        'title': f'Don du {don.date_planifiee.strftime("%d/%m/%Y")} - HEMODON-JIM',
        'active_page': 'dons',
    }
    return render(request, 'dons/detail.html', context)


@login_required
def don_annuler(request, don_id):
    """Annuler un don"""
    don = get_object_or_404(Don, id=don_id, donneur=request.user)
    
    if request.method == 'POST':
        if don.peut_annuler():
            don.statut = 'annule'
            don.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Don',
                objet_id=don.id,
                objet_repr=f"Don #{don.id}",
                details={'statut': 'annule'}
            )
            
            messages.success(request, f"Votre don du {don.date_planifiee.strftime('%d/%m/%Y')} a été annulé.")
        else:
            messages.error(request, "Ce don ne peut pas être annulé.")
        return redirect('dons:my_dons')
    
    context = {
        'don': don,
        'title': f'Annuler le don - HEMODON-JIM',
        'active_page': 'dons',
    }
    return render(request, 'dons/confirm_delete.html', context)


@login_required
def don_update(request, don_id):
    """Mettre à jour un don (admin seulement)"""
    if request.user.groupe not in ['admin', 'pnts'] and not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les droits pour modifier un don.")
        return redirect('dons:my_dons')
    
    don = get_object_or_404(Don, id=don_id)
    
    if request.method == 'POST':
        form = DonUpdateForm(request.POST, instance=don)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Don',
                objet_id=don.id,
                objet_repr=f"Don #{don.id}",
                details={'statut': don.statut}
            )
            
            messages.success(request, f"Don #{don.id} mis à jour avec succès.")
            return redirect('dons:my_dons')
    else:
        form = DonUpdateForm(instance=don)
    
    context = {
        'form': form,
        'don': don,
        'title': f'Modifier le don #{don.id}',
        'active_page': 'dons',
    }
    return render(request, 'dons/update.html', context)