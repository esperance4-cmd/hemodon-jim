from django.db import models
from apps.centres.models import Centre

class Stock(models.Model):
    """Modèle des stocks de sang"""
    
    GROUPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    centre = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_CHOICES)
    quantite_disponible = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.centre.nom} - {self.groupe_sanguin} : {self.quantite_disponible} poches"
    
    def est_en_alerte(self):
        return self.quantite_disponible <= self.seuil_alerte
    
    class Meta:
        db_table = 'stocks'
        unique_together = ('centre', 'groupe_sanguin')
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        ordering = ['centre__nom', 'groupe_sanguin']