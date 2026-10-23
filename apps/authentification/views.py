# apps/authentification/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db import models
from .models import User
from .forms import UserRegistrationForm, UserProfileForm

def home(request):
    """Page d'accueil"""
    return render(request, 'pages/home.html')

@login_required
def dashboard(request):
    """Tableau de bord"""
    context = {
        'user': request.user,
    }
    return render(request, 'pages/dashboard.html', context)

def register(request):
    """Inscription"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie !')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def profile(request):
    """Profil utilisateur avec édition"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'auth/profile.html', {
        'user': request.user,
        'form': form
    })