# apps/profiles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from apps.authentification.models import User
from .models import Profile

# ========== PROFIL UTILISATEUR ==========

@login_required
def profile_view(request, username=None):
    """Vue du profil utilisateur"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Récupérer ou créer le profil
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'can_edit': request.user == user or request.user.is_superuser,
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def profile_edit_view(request):
    """Vue d'édition du profil"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Ici vous traiterez le formulaire d'édition
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('profiles:profile_detail', username=request.user.username)
    
    return render(request, 'profiles/profile_edit.html', {'profile': profile})

# ========== GESTION DES UTILISATEURS (ADMIN) ==========

def is_admin_or_super_admin(user):
    """Vérifie si l'utilisateur est admin ou super admin"""
    return user.is_superuser or (hasattr(user, 'groupe') and user.groupe in ['admin', 'pnts'])

@login_required
@user_passes_test(is_admin_or_super_admin)
def users_list_view(request):
    """Liste des utilisateurs (admin)"""
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role_filter:
        users = users.filter(groupe=role_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'query': query,
        'role_filter': role_filter,
        'roles': User.GROUPE_CHOICES,
    }
    return render(request, 'profiles/users_list.html', context)

@login_required
@user_passes_test(is_admin_or_super_admin)
def user_detail_view(request, user_id):
    """Détail d'un utilisateur (admin)"""
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
    }
    return render(request, 'profiles/user_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_edit_view(request, user_id):
    """Modifier un utilisateur (admin)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Logique de modification
        messages.success(request, f'Utilisateur {user.username} mis à jour avec succès.')
        return redirect('profiles:user_detail', user_id=user.id)
    
    return render(request, 'profiles/user_edit.html', {'profile_user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete_view(request, user_id):
    """Supprimer un utilisateur (admin)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
            return redirect('profiles:users_list')
        
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès.')
        return redirect('profiles:users_list')
    
    return render(request, 'profiles/user_delete.html', {'profile_user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_role_change_view(request, user_id):
    """Changer le rôle d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Logique de changement de rôle
        messages.success(request, f'Rôle de {user.username} changé avec succès.')
        return redirect('profiles:user_detail', user_id=user.id)
    
    return render(request, 'profiles/user_role.html', {'profile_user': user})

# ========== API ENDPOINTS ==========

@login_required
def api_eligibility_check(request):
    """Vérifier l'éligibilité d'un utilisateur (API)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'eligible': True,
        'reason': 'OK',
        'total_donations': 0,
        'lives_saved': 0,
        'last_donation': None,
    })

@login_required
def api_user_stats(request, user_id=None):
    """Statistiques d'un utilisateur (API)"""
    if user_id:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    
    return JsonResponse({
        'username': user.username,
        'full_name': user.get_full_name(),
        'blood_group': user.groupe_sanguin,
        'total_donations': 0,
        'lives_saved': 0,
        'last_donation': None,
    })

# ========== AUTHENTIFICATION (si nécessaire) ==========

def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Logique d'inscription
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        from django.contrib.auth import login
        login(request, user)
        messages.success(request, 'Inscription réussie !')
        return redirect('dashboard')
    
    return render(request, 'profiles/register.html')

def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bonjour {user.username} !')
            return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'profiles/login.html')

def logout_view(request):
    """Vue de déconnexion"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')