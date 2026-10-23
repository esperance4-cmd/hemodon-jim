from django.db import models
from apps.authentification.models import User
from apps.centres.models import Centre
from apps.demandes.models import Demande

class Notification(models.Model):
    """Modèle pour les notifications"""
    
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Alerte'),
        ('danger', 'Urgent'),
        ('system', 'Système'),
    ]
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    est_lue = models.BooleanField(default=False)
    pour_tous = models.BooleanField(default=True)
    utilisateurs = models.ManyToManyField(User, blank=True, related_name='notifications')
    lien = models.CharField(max_length=200, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.titre} - {self.date_creation.strftime('%d/%m/%Y %H:%M')}"


class AuditLog(models.Model):
    """Journal des actions"""
    
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('export', 'Exportation'),
        ('import', 'Importation'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    modele = models.CharField(max_length=100)
    objet_id = models.IntegerField(null=True, blank=True)
    objet_repr = models.CharField(max_length=200)
    details = models.JSONField(default=dict, blank=True)
    ip_adresse = models.GenericIPAddressField(null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_action']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaux'
    
    def __str__(self):
        return f"{self.utilisateur} - {self.action} - {self.modele} - {self.date_action.strftime('%d/%m/%Y %H:%M')}"


class ParametreSysteme(models.Model):
    """Paramètres de l'application"""
    
    cle = models.CharField(max_length=100, unique=True)
    valeur = models.TextField()
    description = models.TextField(blank=True, null=True)
    modifiable = models.BooleanField(default=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paramètre système'
        verbose_name_plural = 'Paramètres système'
    
    def __str__(self):
        return f"{self.cle} = {self.valeur[:50]}"