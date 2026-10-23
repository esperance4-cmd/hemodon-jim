# apps/authentification/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    GROUPE_CHOICES = [
        ('donneur', 'Donneur'),
        ('hospitalier', 'Personnel Hospitalier'),
        ('admin', 'Administrateur'),
        ('pnts', 'PNTS'),
    ]
    
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    groupe = models.CharField(max_length=20, choices=GROUPE_CHOICES, default='donneur')
    telephone = models.CharField(max_length=20, unique=True)
    adresse = models.TextField(blank=True, null=True)
    commune = models.CharField(max_length=100, blank=True, null=True)
    departement = models.CharField(max_length=100, blank=True, null=True)
    date_naissance = models.DateField(null=True, blank=True)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES, blank=True, null=True)
    est_eligible = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} - {self.groupe}"

    def is_super_admin(self):
        """Vérifie si l'utilisateur est un super admin"""
        return self.is_superuser or (hasattr(self, 'groupe') and self.groupe == 'admin')

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'