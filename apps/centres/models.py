from django.db import models

from apps.authentification.models import User 

class Centre(models.Model):
    TYPE_CHOICES = [
        ('public', 'Public'),
        ('prive', 'Privé'),
        ('ong', 'ONG'),
    ]
    
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    adresse = models.TextField()
    commune = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacite_journaliere = models.IntegerField(default=50)
    horaires = models.TextField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='centre_responsable'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'centres'
        verbose_name = 'Centre'
        verbose_name_plural = 'Centres'