# apps/profiles/models.py
from django.db import models
from django.conf import settings

class Profile(models.Model):
    """
    Profil étendu pour les utilisateurs
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'
    
    def __str__(self):
        return f"Profil de {self.user.username}"

class UserActivityLog(models.Model):
    """
    Journal des activités utilisateur
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Journal d\'activité'
        verbose_name_plural = 'Journaux d\'activité'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"