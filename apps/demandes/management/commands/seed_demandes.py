from django.core.management.base import BaseCommand
from apps.demandes.models import Demande
from apps.authentification.models import User
from apps.centres.models import Centre
import random


class Command(BaseCommand):
    help = 'Crée des demandes fictives pour la démonstration'

    def handle(self, *args, **options):
        user = User.objects.first()
        centres = list(Centre.objects.all())

        if not centres:
            self.stdout.write(self.style.ERROR("❌ Aucun centre ! Créez d'abord des centres."))
            return
        if not user:
            self.stdout.write(self.style.ERROR("❌ Aucun utilisateur ! Créez d'abord un utilisateur."))
            return

        groupes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for i in range(5):
            d = Demande.objects.create(
                demandeur=user,
                centre_destination=random.choice(centres),
                groupe_sanguin=random.choice(groupes),
                quantite_necessaire=random.randint(1, 5),
                urgence=random.choice([True, False]),
                statut='en_attente',
                notes=f'Demande de démonstration #{i+1}',
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Demande créée : ID={d.id}, Groupe={d.groupe_sanguin}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Total : {Demande.objects.count()} demandes"))