from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from twilio.rest import Client
from .models import Notification, NotificationTemplate
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service pour gérer tous les types de notifications"""
    
    @staticmethod
    def send_email(user, subject, message, html_content=None):
        """Envoyer un email"""
        try:
            if html_content:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            
            # Enregistrer la notification
            Notification.objects.create(
                user=user,
                type='email',
                title=subject,
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            return True
        except Exception as e:
            logger.error(f"Erreur d'envoi d'email à {user.email}: {e}")
            Notification.objects.create(
                user=user,
                type='email',
                title=subject,
                message=message,
                status='failed',
                metadata={'error': str(e)}
            )
            return False
    
    @staticmethod
    def send_sms(user, message):
        """Envoyer un SMS avec Twilio"""
        try:
            if not hasattr(user, 'phone_number') or not user.phone_number:
                logger.warning(f"Numéro de téléphone manquant pour {user.email}")
                return False
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=user.phone_number
            )
            
            Notification.objects.create(
                user=user,
                type='sms',
                title='SMS Notification',
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            return True
        except Exception as e:
            logger.error(f"Erreur d'envoi SMS à {user.phone_number}: {e}")
            Notification.objects.create(
                user=user,
                type='sms',
                title='SMS Notification',
                message=message,
                status='failed',
                metadata={'error': str(e)}
            )
            return False
    
    @staticmethod
    def send_in_app_notification(user, title, message, metadata=None):
        """Créer une notification in-app"""
        notification = Notification.objects.create(
            user=user,
            type='in_app',
            title=title,
            message=message,
            status='pending',
            metadata=metadata or {}
        )
        return notification
    
    @staticmethod
    def send_notification_from_template(user, template_name, context, send_method='email'):
        """Envoyer une notification à partir d'un template"""
        try:
            template = NotificationTemplate.objects.get(name=template_name)
            
            # Rendre les messages avec le contexte
            subject = template.subject.format(**context)
            body = template.body.format(**context)
            
            if send_method == 'email':
                html_content = render_to_string(
                    f'notifications/emails/{template_name}.html',
                    context
                )
                return NotificationService.send_email(user, subject, body, html_content)
            elif send_method == 'sms':
                return NotificationService.send_sms(user, body)
            else:
                return NotificationService.send_in_app_notification(user, subject, body)
                
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template {template_name} non trouvé")
            return False
        except Exception as e:
            logger.error(f"Erreur d'envoi de notification: {e}")
            return False


class DonationNotificationService:
    """Notifications spécifiques aux dons de sang"""
    
    @staticmethod
    def notify_donation_reminder(profile, days_before=7):
        """Envoyer un rappel de don"""
        user = profile.user
        context = {
            'user': user,
            'profile': profile,
            'days': days_before,
            'donation_date': profile.last_donation_date,
        }
        
        NotificationService.send_notification_from_template(
            user,
            'donation_reminder',
            context,
            'email'
        )
    
    @staticmethod
    def notify_donation_eligibility(profile):
        """Notifier l'éligibilité au don"""
        user = profile.user
        context = {
            'user': user,
            'profile': profile,
        }
        
        NotificationService.send_notification_from_template(
            user,
            'donation_eligibility',
            context,
            'email'
        )
    
    @staticmethod
    def notify_blood_shortage(blood_group, users_list):
        """Notifier une pénurie de sang"""
        for user in users_list:
            context = {
                'user': user,
                'blood_group': blood_group,
            }
            NotificationService.send_notification_from_template(
                user,
                'blood_shortage_alert',
                context,
                'email'
            )
    
    @staticmethod
    def notify_urgent_donation_needed(blood_group, users_list):
        """Notifier un besoin urgent de don"""
        for user in users_list:
            context = {
                'user': user,
                'blood_group': blood_group,
            }
            NotificationService.send_notification_from_template(
                user,
                'urgent_donation_needed',
                context,
                'email'
            )
    
    @staticmethod
    def notify_appointment_confirmation(user, appointment):
        """Confirmer un rendez-vous"""
        context = {
            'user': user,
            'appointment': appointment,
            'date': appointment.date,
            'center': appointment.center_name,
        }
        
        # Envoyer email
        NotificationService.send_notification_from_template(
            user,
            'appointment_confirmation',
            context,
            'email'
        )
        
        # Envoyer SMS si numéro disponible
        if hasattr(user, 'phone_number') and user.phone_number:
            NotificationService.send_notification_from_template(
                user,
                'appointment_confirmation_sms',
                context,
                'sms'
            )