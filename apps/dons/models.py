from django.db import models
from django.utils import timezone
from apps.authentification.models import User
from apps.centres.models import Centre

class Don(models.Model):
    """Modèle des dons de sang"""
    
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('effectue', 'Effectué'),
        ('annule', 'Annulé'),
        ('reporte', 'Reporté'),
    ]
    
    donneur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dons'
    )
    centre = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name='dons'
    )
    date_planifiee = models.DateTimeField()
    date_effectuee = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    quantite = models.IntegerField(default=450, help_text="Quantité en ml")
    observations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.donneur.username} - {self.centre.nom} - {self.date_planifiee.strftime('%d/%m/%Y')}"
    
    def est_effectue(self):
        return self.statut == 'effectue'
    
    def peut_annuler(self):
        return self.statut == 'planifie' and timezone.now() < self.date_planifiee
    
    class Meta:
        db_table = 'dons'
        verbose_name = 'Don'
        verbose_name_plural = 'Dons'
        ordering = ['-date_planifiee']