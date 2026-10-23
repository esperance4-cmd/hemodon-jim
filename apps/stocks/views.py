from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import Stock
from apps.centres.models import Centre
from .forms import StockUpdateForm, StockBulkUpdateForm
from apps.app_admin.models import AuditLog


def stocks_list(request):
    """Liste globale des stocks de tous les centres"""
    stocks = Stock.objects.select_related('centre').all().order_by('centre__nom', 'groupe_sanguin')
    
    # Filtres
    centre_id = request.GET.get('centre')
    if centre_id:
        stocks = stocks.filter(centre_id=centre_id)
    
    groupe = request.GET.get('groupe')
    if groupe:
        stocks = stocks.filter(groupe_sanguin=groupe)
    
    en_alerte = request.GET.get('alerte') == 'true'
    if en_alerte:
        stocks = stocks.filter(quantite_disponible__lte=F('seuil_alerte'))
    
    # Recherche par centre
    search = request.GET.get('search')
    if search:
        stocks = stocks.filter(centre__nom__icontains=search)
    
    # Pagination
    paginator = Paginator(stocks, 30)
    page_number = request.GET.get('page')
    stocks_page = paginator.get_page(page_number)
    
    # Statistiques globales
    stats = {
        'total_poches': Stock.objects.aggregate(total=Sum('quantite_disponible'))['total'] or 0,
        'centres_actifs': Centre.objects.filter(est_actif=True).count(),
        'stocks_alertes': Stock.objects.filter(quantite_disponible__lte=F('seuil_alerte')).count(),
        'groupes_disponibles': Stock.objects.filter(quantite_disponible__gt=0).values('groupe_sanguin').distinct().count(),
    }
    
    context = {
        'stocks': stocks_page,
        'centres': Centre.objects.filter(est_actif=True),
        'groupes': Stock.GROUPE_CHOICES,
        'stats': stats,
        'title': 'Stocks de sang - HEMODON-JIM',
        'active_page': 'stocks',
    }
    return render(request, 'stocks/list.html', context)


def stocks_centre(request, centre_id):
    """Stocks d'un centre spécifique"""
    centre = get_object_or_404(Centre, id=centre_id, est_actif=True)
    stocks = Stock.objects.filter(centre=centre)
    
    # Vérifier si le centre a des alertes
    alertes = stocks.filter(quantite_disponible__lte=F('seuil_alerte'))
    
    # Statistiques du centre
    stats = {
        'total_poches': stocks.aggregate(total=Sum('quantite_disponible'))['total'] or 0,
        'groupes_disponibles': stocks.filter(quantite_disponible__gt=0).count(),
        'alertes': alertes.count(),
    }
    
    context = {
        'centre': centre,
        'stocks': stocks,
        'alertes': alertes,
        'stats': stats,
        'title': f'Stocks - {centre.nom}',
        'active_page': 'stocks',
    }
    return render(request, 'stocks/centre.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def stock_update(request, stock_id):
    """Mettre à jour un stock (admin seulement)"""
    stock = get_object_or_404(Stock, id=stock_id)
    
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=stock)
        if form.is_valid():
            ancienne_quantite = stock.quantite_disponible
            form.save()
            
            AuditLog.objects.create(
                utilisateur=request.user,
                action='update',
                modele='Stock',
                objet_id=stock.id,
                objet_repr=f"{stock.centre.nom} - {stock.groupe_sanguin}",
                details={
                    'ancienne_quantite': ancienne_quantite,
                    'nouvelle_quantite': stock.quantite_disponible
                }
            )
            
            messages.success(request, f"Stock mis à jour avec succès.")
            return redirect('stocks:list')
    else:
        form = StockUpdateForm(instance=stock)
    
    context = {
        'form': form,
        'stock': stock,
        'title': f'Mettre à jour - {stock.centre.nom} {stock.groupe_sanguin}',
        'active_page': 'stocks',
    }
    return render(request, 'stocks/update.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groupe in ['admin', 'pnts'])
def stock_bulk_update(request):
    """Mise à jour groupée des stocks (admin seulement)"""
    if request.method == 'POST':
        form = StockBulkUpdateForm(request.POST)
        if form.is_valid():
            centre = form.cleaned_data['centre']
            groupe = form.cleaned_data['groupe_sanguin']
            quantite = form.cleaned_data['quantite']
            
            stock = Stock.objects.filter(centre=centre, groupe_sanguin=groupe).first()
            if stock:
                stock.quantite_disponible = quantite
                stock.save()
                
                AuditLog.objects.create(
                    utilisateur=request.user,
                    action='update',
                    modele='Stock',
                    objet_repr=f"{centre.nom} - {groupe} (bulk)",
                    details={'quantite': quantite}
                )
                
                messages.success(request, f"Stock mis à jour avec succès.")
            else:
                messages.error(request, "Stock non trouvé.")
            
            return redirect('stocks:list')
    else:
        form = StockBulkUpdateForm()
    
    context = {
        'form': form,
        'title': 'Mise à jour groupée des stocks',
        'active_page': 'stocks',
    }
    return render(request, 'stocks/bulk_update.html', context)


def stocks_alertes(request):
    """Page des alertes de stocks critiques"""
    stocks = Stock.objects.filter(
        quantite_disponible__lte=F('seuil_alerte')
    ).select_related('centre').order_by('centre__nom', 'groupe_sanguin')
    
    # Groupes par centre
    centres_alertes = {}
    for stock in stocks:
        if stock.centre.nom not in centres_alertes:
            centres_alertes[stock.centre.nom] = []
        centres_alertes[stock.centre.nom].append(stock)
    
    context = {
        'centres_alertes': centres_alertes,
        'total_alertes': stocks.count(),
        'title': 'Alertes stocks - HEMODON-JIM',
        'active_page': 'stocks',
    }
    return render(request, 'stocks/alerte.html', context)


def stocks_api(request):
    """API pour récupérer les stocks (format JSON)"""
    centre_id = request.GET.get('centre')
    groupe = request.GET.get('groupe')
    
    stocks = Stock.objects.select_related('centre').all()
    
    if centre_id:
        stocks = stocks.filter(centre_id=centre_id)
    if groupe:
        stocks = stocks.filter(groupe_sanguin=groupe)
    
    data = []
    for stock in stocks:
        data.append({
            'id': stock.id,
            'centre': stock.centre.nom,
            'centre_id': stock.centre.id,
            'groupe_sanguin': stock.groupe_sanguin,
            'quantite_disponible': stock.quantite_disponible,
            'seuil_alerte': stock.seuil_alerte,
            'est_en_alerte': stock.quantite_disponible <= stock.seuil_alerte,
            'date_mise_a_jour': stock.date_mise_a_jour.strftime('%d/%m/%Y %H:%M'),
        })
    
    return JsonResponse(data, safe=False)