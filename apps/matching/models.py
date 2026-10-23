from django.db import models
from django.utils import timezone
from apps.authentification.models import User
from apps.centres.models import Centre
from apps.demandes.models import Demande
from apps.dons.models import Don


class MatchSuggestion(models.Model):
    """Proposition de matching donneur/demande"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('notifie', 'Notifié'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('expire', 'Expiré'),
        ('traite', 'Traité'),
    ]
    
    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name='matchs'
    )
    donneur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matchs'
    )
    centre = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name='matchs'
    )
    score = models.FloatField(
        default=0,
        help_text="Score de compatibilité (0-100)"
    )
    distance_km = models.FloatField(
        null=True,
        blank=True,
        help_text="Distance en km entre le donneur et le centre"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    date_suggestion = models.DateTimeField(auto_now_add=True)
    date_notification = models.DateTimeField(null=True, blank=True)
    date_reponse = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-score', '-date_suggestion']
        verbose_name = 'Match suggestion'
        verbose_name_plural = 'Match suggestions'
        unique_together = ('demande', 'donneur')
    
    def __str__(self):
        return f"Match #{self.id} - {self.donneur.username} vs Demande #{self.demande.id}"
    
    def notifier(self):
        """Marquer comme notifié"""
        self.statut = 'notifie'
        self.date_notification = timezone.now()
        self.save()
    
    def accepter(self):
        """Accepter le match"""
        self.statut = 'accepte'
        self.date_reponse = timezone.now()
        self.save()
    
    def refuser(self):
        """Refuser le match"""
        self.statut = 'refuse'
        self.date_reponse = timezone.now()
        self.save()
    
    def est_valide(self):
        """Vérifier si le match est toujours valide"""
        return self.statut in ['en_attente', 'notifie']


class MatchingLog(models.Model):
    """Journal des opérations de matching"""
    
    ACTION_CHOICES = [
        ('auto', 'Automatique'),
        ('manuel', 'Manuel'),
        ('cron', 'Programmé'),
    ]
    
    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name='matching_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    nb_suggestions = models.IntegerField(default=0)
    details = models.JSONField(default=dict, blank=True)
    date_execution = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_execution']
        verbose_name = 'Matching log'
        verbose_name_plural = 'Matching logs'
    
    def __str__(self):
        return f"Log #{self.id} - Demande #{self.demande.id} - {self.action}"