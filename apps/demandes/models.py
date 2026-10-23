from django.db import models
from django.utils import timezone
from apps.authentification.models import User
from apps.centres.models import Centre

class Demande(models.Model):
    """Modèle des demandes de sang"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('traitee', 'Traitée'),
        ('urgente', 'Urgente'),
        ('annulee', 'Annulée'),
    ]
    
    GROUPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    demandeur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='demandes'
    )
    centre_source = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name='demandes_sortantes',
        null=True,
        blank=True,
        help_text="Centre qui fait la demande"
    )
    centre_destination = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name='demandes_entrantes',
        help_text="Centre qui recevra le sang"
    )
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_CHOICES)
    quantite_necessaire = models.IntegerField(help_text="Nombre de poches nécessaires")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    urgence = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Demande #{self.id} - {self.groupe_sanguin} - {self.statut}"
    
    def est_urgente(self):
        return self.urgence and self.statut in ['en_attente', 'en_cours']
    
    def temps_attente(self):
        if self.date_traitement:
            delta = self.date_traitement - self.date_demande
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    class Meta:
        db_table = 'demandes'
        verbose_name = 'Demande'
        verbose_name_plural = 'Demandes'
        ordering = ['-date_demande']