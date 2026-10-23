from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.db import models
from django.views.decorators.http import require_http_methods
import csv
from datetime import datetime

from apps.authentification.models import User
from apps.centres.models import Centre
from apps.stocks.models import Stock
from apps.dons.models import Don
from apps.demandes.models import Demande
from .models import Notification, AuditLog, ParametreSysteme

from .forms import (
    UserAdminForm,
    CentreAdminForm,
    StockAdminForm,
    DemandeAdminForm,
    NotificationForm,
    NotificationFilterForm
)

# ============================================
# VÉRIFICATION ADMIN
# ============================================

def is_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_authenticated and (user.is_superuser or user.groupe in ['admin', 'pnts'])


# ============================================
# TABLEAU DE BORD
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Tableau de bord de l'administration"""
    
    # Statistiques générales
    stats = {
        'total_donneurs': User.objects.filter(groupe='donneur').count(),
        'total_centres': Centre.objects.filter(est_actif=True).count(),
        'total_dons': Don.objects.filter(statut='effectue').count(),
        'total_demandes': Demande.objects.count(),
        'demandes_urgentes': Demande.objects.filter(urgence=True, statut__in=['en_attente', 'en_cours']).count(),
        'stocks_critiques': Stock.objects.filter(quantite_disponible__lte=F('seuil_alerte')).count(),
        'nouveaux_donneurs_mois': User.objects.filter(
            groupe='donneur',
            date_joined__month=timezone.now().month
        ).count(),
    }
    
    # Dons par mois (6 derniers mois)
    dons_par_mois = []
    for i in range(6, 0, -1):
        mois = timezone.now().month - i
        annee = timezone.now().year
        if mois <= 0:
            mois += 12
            annee -= 1
        count = Don.objects.filter(
            date_effectuee__year=annee,
            date_effectuee__month=mois,
            statut='effectue'
        ).count()
        dons_par_mois.append({
            'mois': datetime(annee, mois, 1).strftime('%B'),
            'count': count
        })
    
    # Demandes par statut
    demandes_statut = Demande.objects.values('statut').annotate(count=Count('id'))
    
    # Dernières notifications
    notifications = Notification.objects.all()[:10]
    
    # Dernières actions
    logs = AuditLog.objects.select_related('utilisateur').all()[:10]
    
    context = {
        'stats': stats,
        'dons_par_mois': dons_par_mois,
        'demandes_statut': demandes_statut,
        'notifications': notifications,
        'logs': logs,
        'title': 'Tableau de bord - Administration',
        'active_page': 'dashboard',
    }
    return render(request, 'app_admin/dashboard.html', context)


# ============================================
# GESTION DES UTILISATEURS
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Liste des utilisateurs"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtres
    groupe = request.GET.get('groupe')
    if groupe:
        users = users.filter(groupe=groupe)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'groupes': User.GROUPE_CHOICES,
        'title': 'Gestion des utilisateurs',
        'active_page': 'users',
    }
    return render(request, 'app_admin/users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Détail d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    dons = Don.objects.filter(donneur=user).order_by('-date_planifiee')[:10]
    demandes = Demande.objects.filter(demandeur=user).order_by('-date_demande')[:10]
    
    context = {
        'user': user,
        'dons': dons,
        'demandes': demandes,
        'title': f'Utilisateur - {user.username}',
        'active_page': 'users',
    }
    return render(request, 'app_admin/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_toggle(request, user_id):
    """Activer/Désactiver un utilisateur"""
    if request.method != 'POST':
        return redirect('admin_users')
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    AuditLog.objects.create(
        utilisateur=request.user,
        action='update',
        modele='User',
        objet_id=user.id,
        objet_repr=str(user),
        details={'is_active': user.is_active}
    )
    
    messages.success(request, f"Utilisateur {user.username} {'activé' if user.is_active else 'désactivé'} avec succès.")
    return redirect('admin_user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Modifier un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='User',
                objet_id=user.id,
                objet_repr=str(user),
                details={'username': user.username}
            )
            
            messages.success(request, f"Utilisateur {user.username} modifié avec succès.")
            return redirect('app_admin:user_detail', user_id=user.id)
    else:
        form = UserAdminForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': f'Modifier - {user.username}',
        'active_page': 'users',
    }
    return render(request, 'app_admin/user_edit.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        AuditLog.objects.create(
            utilisateur=request.user,
            action='delete',
            modele='User',
            objet_id=user_id,
            objet_repr=username,
            details={'username': username}
        )
        
        messages.success(request, f"Utilisateur {username} supprimé avec succès.")
        return redirect('admin_users')
    
    return render(request, 'app_admin/confirm_delete.html', {
        'object': user,
        'title': 'Supprimer l\'utilisateur',
        'back_url': 'admin_users',
        'active_page': 'users',
    })


# ============================================
# GESTION DES CENTRES
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_centres(request):
    """Liste des centres"""
    centres = Centre.objects.all().order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        centres = centres.filter(
            Q(nom__icontains=search) |
            Q(commune__icontains=search) |
            Q(departement__icontains=search)
        )
    
    paginator = Paginator(centres, 20)
    page_number = request.GET.get('page')
    centres_page = paginator.get_page(page_number)
    
    context = {
        'centres': centres_page,
        'title': 'Gestion des centres',
        'active_page': 'centres',
    }
    return render(request, 'app_admin/centres.html', context)


@login_required
@user_passes_test(is_admin)
def admin_centre_create(request):
    """Créer un centre"""
    if request.method == 'POST':
        form = CentreAdminForm(request.POST)
        if form.is_valid():
            centre = form.save(commit=False)
            centre.responsable = request.user
            centre.save()
            
            # Créer les stocks initiaux
            for groupe in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
                Stock.objects.create(
                    centre=centre,
                    groupe_sanguin=groupe,
                    quantite_disponible=0,
                    seuil_alerte=5
                )
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='create',
                modele='Centre',
                objet_id=centre.id,
                objet_repr=centre.nom,
                details={'nom': centre.nom}
            )
            
            messages.success(request, f"Centre {centre.nom} créé avec succès.")
            return redirect('admin_centres')
    else:
        form = CentreAdminForm()
    
    context = {
        'form': form,
        'title': 'Créer un centre',
        'active_page': 'centres',
        'action': 'create',
    }
    return render(request, 'app_admin/centre_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_centre_edit(request, centre_id):
    """Modifier un centre"""
    centre = get_object_or_404(Centre, id=centre_id)
    
    if request.method == 'POST':
        form = CentreAdminForm(request.POST, instance=centre)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Centre',
                objet_id=centre.id,
                objet_repr=centre.nom,
                details={'nom': centre.nom}
            )
            
            messages.success(request, f"Centre {centre.nom} modifié avec succès.")
            return redirect('admin_centres')
    else:
        form = CentreAdminForm(instance=centre)
    
    context = {
        'form': form,
        'centre': centre,
        'title': f'Modifier - {centre.nom}',
        'active_page': 'centres',
        'action': 'edit',
    }
    return render(request, 'app_admin/centre_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_centre_delete(request, centre_id):
    """Supprimer un centre"""
    centre = get_object_or_404(Centre, id=centre_id)
    
    if request.method == 'POST':
        nom = centre.nom
        centre.delete()
        
        AuditLog.objects.create(
            utilisateur=request.user,
            action='delete',
            modele='Centre',
            objet_id=centre_id,
            objet_repr=nom,
            details={'nom': nom}
        )
        
        messages.success(request, f"Centre {nom} supprimé avec succès.")
        return redirect('admin_centres')
    
    return render(request, 'app_admin/confirm_delete.html', {
        'object': centre,
        'title': 'Supprimer le centre',
        'back_url': 'admin_centres',
        'active_page': 'centres',
    })


# ============================================
# GESTION DES STOCKS
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_stocks(request):
    """Gestion des stocks"""
    stocks = Stock.objects.select_related('centre').all().order_by('centre__nom', 'groupe_sanguin')
    
    centre_id = request.GET.get('centre')
    if centre_id:
        stocks = stocks.filter(centre_id=centre_id)
    
    groupes = request.GET.get('groupe')
    if groupes:
        stocks = stocks.filter(groupe_sanguin=groupes)
    
    en_alerte = request.GET.get('alerte') == 'true'
    if en_alerte:
        stocks = stocks.filter(quantite_disponible__lte=F('seuil_alerte'))
    
    context = {
        'stocks': stocks,
        'centres': Centre.objects.filter(est_actif=True),
        'groupes': Stock.GROUPE_CHOICES,
        'title': 'Gestion des stocks',
        'active_page': 'stocks',
    }
    return render(request, 'app_admin/stocks.html', context)


@login_required
@user_passes_test(is_admin)
def admin_stock_update(request, stock_id):
    """Mettre à jour un stock"""
    stock = get_object_or_404(Stock, id=stock_id)
    
    if request.method == 'POST':
        form = StockAdminForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Stock',
                objet_id=stock.id,
                objet_repr=f"{stock.centre.nom} - {stock.groupe_sanguin}",
                details={'quantite': stock.quantite_disponible}
            )
            
            messages.success(request, f"Stock mis à jour avec succès.")
            return redirect('admin_stocks')
    else:
        form = StockAdminForm(instance=stock)
    
    context = {
        'form': form,
        'stock': stock,
        'title': f'Mettre à jour - {stock.centre.nom} {stock.groupe_sanguin}',
        'active_page': 'stocks',
    }
    return render(request, 'app_admin/stock_form.html', context)


# ============================================
# GESTION DES DEMANDES
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_demandes(request):
    """Gestion des demandes"""
    demandes = Demande.objects.select_related('demandeur', 'centre_destination').all().order_by('-date_demande')
    
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    urgence = request.GET.get('urgence')
    if urgence == 'true':
        demandes = demandes.filter(urgence=True)
    
    search = request.GET.get('search')
    if search:
        demandes = demandes.filter(
            Q(demandeur__username__icontains=search) |
            Q(centre_destination__nom__icontains=search)
        )
    
    paginator = Paginator(demandes, 20)
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    context = {
        'demandes': demandes_page,
        'statuts': Demande.STATUT_CHOICES,
        'title': 'Gestion des demandes',
        'active_page': 'demandes',
    }
    return render(request, 'app_admin/demandes.html', context)


@login_required
@user_passes_test(is_admin)
def admin_demande_update(request, demande_id):
    """Mettre à jour une demande"""
    demande = get_object_or_404(Demande, id=demande_id)
    
    if request.method == 'POST':
        form = DemandeAdminForm(request.POST, instance=demande)
        if form.is_valid():
            demande = form.save(commit=False)
            if demande.statut == 'traitee':
                demande.date_traitement = timezone.now()
            demande.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Demande',
                objet_id=demande.id,
                objet_repr=f"Demande #{demande.id}",
                details={'statut': demande.statut}
            )
            
            messages.success(request, f"Demande #{demande.id} mise à jour avec succès.")
            return redirect('admin_demandes')
    else:
        form = DemandeAdminForm(instance=demande)
    
    context = {
        'form': form,
        'demande': demande,
        'statuts': Demande.STATUT_CHOICES,
        'title': f'Mettre à jour la demande #{demande.id}',
        'active_page': 'demandes',
    }
    return render(request, 'app_admin/demande_form.html', context)


# ============================================
# GESTION DES NOTIFICATIONS (ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    """Gestion des notifications"""
    notifications = Notification.objects.all().order_by('-date_creation')
    
    # Filtres
    type_notif = request.GET.get('type')
    if type_notif:
        notifications = notifications.filter(type=type_notif)
    
    lu = request.GET.get('lu')
    if lu == 'true':
        notifications = notifications.filter(est_lue=True)
    elif lu == 'false':
        notifications = notifications.filter(est_lue=False)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications_page,
        'types': Notification.TYPE_CHOICES,
        'title': 'Flux d\'actualités - Notifications',
        'active_page': 'notifications',
    }
    return render(request, 'app_admin/notifications.html', context)


@login_required
@user_passes_test(is_admin)
def admin_notification_create(request):
    """Créer une notification"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='create',
                modele='Notification',
                objet_id=notification.id,
                objet_repr=notification.titre,
                details={
                    'titre': notification.titre,
                    'type': notification.type,
                    'pour_tous': notification.pour_tous,
                    'nombre_utilisateurs': notification.utilisateurs.count() if not notification.pour_tous else 0
                }
            )
            
            messages.success(request, f"Notification '{notification.titre}' créée avec succès.")
            return redirect('app_admin:notifications')
    else:
        form = NotificationForm()
    
    context = {
        'form': form,
        'users': User.objects.filter(is_active=True),
        'title': 'Créer une notification',
        'active_page': 'notifications',
    }
    return render(request, 'app_admin/notification_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_notification_delete(request, notif_id):
    """Supprimer une notification"""
    notification = get_object_or_404(Notification, id=notif_id)
    
    if request.method == 'POST':
        titre = notification.titre
        notification.delete()
        
        AuditLog.objects.create(
            utilisateur=request.user,
            action='delete',
            modele='Notification',
            objet_id=notif_id,
            objet_repr=titre,
            details={'titre': titre}
        )
        
        messages.success(request, f"Notification '{titre}' supprimée avec succès.")
        return redirect('app_admin:notifications')
    
    return render(request, 'app_admin/confirm_delete.html', {
        'object': notification,
        'title': 'Supprimer la notification',
        'back_url': 'app_admin:notifications',
        'active_page': 'notifications',
    })


@login_required
@user_passes_test(is_admin)
def admin_notification_toggle_read(request, notif_id):
    """Marquer comme lu/non lu (admin)"""
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    
    notification = get_object_or_404(Notification, id=notif_id)
    notification.est_lue = not notification.est_lue
    notification.save()
    
    return JsonResponse({
        'success': True,
        'est_lue': notification.est_lue
    })


# ============================================
# NOTIFICATIONS POUR LES UTILISATEURS
# ============================================

@login_required
def user_notifications(request):
    """Liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user)
    ).distinct().order_by('-date_creation')
    
    type_notif = request.GET.get('type')
    if type_notif:
        notifications = notifications.filter(type=type_notif)
    
    lu = request.GET.get('lu')
    if lu == 'true':
        notifications = notifications.filter(est_lue=True)
    elif lu == 'false':
        notifications = notifications.filter(est_lue=False)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    if request.GET.get('mark_read') == 'all':
        notifications.filter(est_lue=False).update(est_lue=True)
        messages.success(request, "Toutes les notifications ont été marquées comme lues.")
        return redirect('user_notifications')
    
    non_lues = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().count()
    
    context = {
        'notifications': notifications_page,
        'types': Notification.TYPE_CHOICES,
        'non_lues': non_lues,
        'title': 'Mes notifications - HEMODON-JIM',
        'active_page': 'notifications',
    }
    return render(request, 'notifications/list.html', context)


@login_required
def user_notification_mark_read(request, notif_id):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notif_id)
    
    # Vérifier que l'utilisateur a accès à cette notification
    if not (notification.pour_tous or notification.utilisateurs.filter(id=request.user.id).exists()):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    if request.method == 'POST':
        notification.est_lue = True
        notification.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=405)


@login_required
def user_notification_mark_all_read(request):
    """Marquer toutes les notifications comme lues"""
    if request.method == 'POST':
        Notification.objects.filter(
            Q(pour_tous=True) | Q(utilisateurs=request.user),
            est_lue=False
        ).update(est_lue=True)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=405)


@login_required
def user_notifications_count(request):
    """Récupérer le nombre de notifications non lues"""
    count = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().count()
    
    return JsonResponse({'count': count})


@login_required
def user_notifications_badge(request):
    """Partial pour le badge de notifications"""
    count = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().count()
    
    recent = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().order_by('-date_creation')[:5]
    
    context = {
        'count': count,
        'recent': recent,
        'user': request.user,
    }
    return render(request, 'notifications/badge.html', context)



# ============================================
# BADGE DE NOTIFICATIONS (PARTIAL)
# ============================================

@login_required
def user_notifications_badge(request):
    """Partial pour le badge de notifications"""
    count = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().count()
    
    recent = Notification.objects.filter(
        Q(pour_tous=True) | Q(utilisateurs=request.user),
        est_lue=False
    ).distinct().order_by('-date_creation')[:5]
    
    context = {
        'count': count,
        'recent': recent,
        'user': request.user,
    }
    return render(request, 'notifications/badge.html', context)


# ============================================
# JOURNAUX (LOGS)
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_logs(request):
    """Consultation des journaux"""
    logs = AuditLog.objects.select_related('utilisateur').all().order_by('-date_action')
    
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    modele = request.GET.get('modele')
    if modele:
        logs = logs.filter(modele=modele)
    
    utilisateur = request.GET.get('utilisateur')
    if utilisateur:
        logs = logs.filter(utilisateur__username__icontains=utilisateur)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)
    
    context = {
        'logs': logs_page,
        'actions': AuditLog.ACTION_CHOICES,
        'modeles': AuditLog.objects.values_list('modele', flat=True).distinct(),
        'title': 'Journal des actions',
        'active_page': 'logs',
    }
    return render(request, 'app_admin/logs.html', context)


# ============================================
# RAPPORTS ET STATISTIQUES
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Rapports et statistiques avancées"""
    
    total_donneurs = User.objects.filter(groupe='donneur').count()
    total_centres = Centre.objects.filter(est_actif=True).count()
    total_dons = Don.objects.filter(statut='effectue').count()
    total_demandes = Demande.objects.count()
    
    dons_par_groupe = Don.objects.filter(
        statut='effectue'
    ).values(
        'donneur__groupe_sanguin'
    ).annotate(count=Count('id')).order_by('-count')
    
    demandes_urgence = Demande.objects.values('urgence').annotate(count=Count('id'))
    
    dons_par_mois = []
    for i in range(11, -1, -1):
        mois = timezone.now().month - i
        annee = timezone.now().year
        if mois <= 0:
            mois += 12
            annee -= 1
        count = Don.objects.filter(
            date_effectuee__year=annee,
            date_effectuee__month=mois,
            statut='effectue'
        ).count()
        dons_par_mois.append({
            'mois': datetime(annee, mois, 1).strftime('%B %Y'),
            'count': count
        })
    
    centres_departement = Centre.objects.values('departement').annotate(count=Count('id'))
    
    taux_conversion = 0
    if total_donneurs > 0:
        dons_uniques = Don.objects.filter(statut='effectue').values('donneur').distinct().count()
        taux_conversion = round((dons_uniques / total_donneurs) * 100, 1)
    
    context = {
        'total_donneurs': total_donneurs,
        'total_centres': total_centres,
        'total_dons': total_dons,
        'total_demandes': total_demandes,
        'dons_par_groupe': dons_par_groupe,
        'demandes_urgence': demandes_urgence,
        'dons_par_mois': dons_par_mois,
        'centres_departement': centres_departement,
        'taux_conversion': taux_conversion,
        'title': 'Rapports et statistiques',
        'active_page': 'reports',
    }
    return render(request, 'app_admin/reports.html', context)


# ============================================
# EXPORTATION DE DONNÉES
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_export(request, modele):
    """Exporter les données en CSV"""
    
    if modele == 'users':
        queryset = User.objects.all()
        filename = 'utilisateurs'
        fields = ['id', 'username', 'email', 'telephone', 'groupe', 'groupe_sanguin', 'is_active', 'date_joined']
        headers = ['ID', 'Nom', 'Email', 'Téléphone', 'Groupe', 'Groupe Sanguin', 'Actif', "Date d'inscription"]
    elif modele == 'centres':
        queryset = Centre.objects.all()
        filename = 'centres'
        fields = ['id', 'nom', 'type', 'commune', 'departement', 'telephone', 'email', 'est_actif']
        headers = ['ID', 'Nom', 'Type', 'Commune', 'Département', 'Téléphone', 'Email', 'Actif']
    elif modele == 'dons':
        queryset = Don.objects.filter(statut='effectue')
        filename = 'dons'
        fields = ['id', 'donneur__username', 'centre__nom', 'date_effectuee', 'quantite']
        headers = ['ID', 'Donneur', 'Centre', 'Date', 'Quantité (ml)']
    elif modele == 'demandes':
        queryset = Demande.objects.all()
        filename = 'demandes'
        fields = ['id', 'demandeur__username', 'groupe_sanguin', 'quantite_necessaire', 'statut', 'date_demande']
        headers = ['ID', 'Demandeur', 'Groupe Sanguin', 'Quantité', 'Statut', 'Date']
    else:
        messages.error(request, "Modèle non supporté pour l'exportation.")
        return redirect('app_admin:dashboard')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(headers)
    
    for obj in queryset:
        row = []
        for field in fields:
            if '__' in field:
                parts = field.split('__')
                value = obj
                for part in parts:
                    value = getattr(value, part, '')
                row.append(str(value) if value else '')
            else:
                value = getattr(obj, field, '')
                if field.endswith('_date') and value:
                    value = value.strftime('%d/%m/%Y %H:%M')
                row.append(str(value) if value else '')
        writer.writerow(row)
    
    AuditLog.objects.create(
        utilisateur=request.user,
        action='export',
        modele=modele.capitalize(),
        details={'modele': modele}
    )
    
    messages.success(request, f"Export {modele} effectué avec succès.")
    return response