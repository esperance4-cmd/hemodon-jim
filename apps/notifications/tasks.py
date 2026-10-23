from celery import shared_task
from django.contrib.auth import get_user_model
from .services import DonationNotificationService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_donation_reminders():
    """Envoyer des rappels de don aux utilisateurs éligibles"""
    from apps.profiles.models import Profile
    
    eligible_profiles = Profile.objects.filter(
        is_donor=True,
        can_donate=True
    )
    
    for profile in eligible_profiles:
        DonationNotificationService.notify_donation_reminder(profile)
    
    logger.info(f"Rappels envoyés à {eligible_profiles.count()} utilisateurs")


@shared_task
def send_blood_shortage_alert(blood_group):
    """Envoyer une alerte de pénurie de sang"""
    # Récupérer les utilisateurs compatibles
    compatible_users = User.objects.filter(
        profile__blood_group__in=get_compatible_groups(blood_group),
        profile__can_donate=True
    )
    
    DonationNotificationService.notify_blood_shortage(blood_group, compatible_users)


@shared_task
def send_weekly_donation_stats():
    """Envoyer les statistiques hebdomadaires"""
    from django.db.models import Count
    from apps.donations.models import Donation
    
    # Statistiques de la semaine
    stats = {
        'total_donations': Donation.objects.filter(created_at__week=timezone.now().isocalendar()[1]).count(),
        'new_donors': User.objects.filter(date_joined__week=timezone.now().isocalendar()[1]).count(),
    }
    
    # Envoyer aux administrateurs
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        context = {'admin': admin, 'stats': stats}
        NotificationService.send_notification_from_template(
            admin,
            'weekly_stats',
            context,
            'email'
        )


def get_compatible_groups(blood_group):
    """Retourner les groupes sanguins compatibles"""
    # À implémenter selon votre système de compatibilité
    compat = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    return compat.get(blood_group, [])