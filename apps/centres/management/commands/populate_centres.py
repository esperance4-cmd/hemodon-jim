from django.core.management.base import BaseCommand
from apps.centres.models import Centre
from apps.stocks.models import Stock


class Command(BaseCommand):
    help = 'Crée des centres de transfusion fictifs pour la démonstration'

    def handle(self, *args, **options):
        centres_data = [
            {
                'nom': 'Hôpital Général de Port-au-Prince',
                'type': 'public',
                'adresse': 'Rue Monseigneur Guilloux',
                'commune': 'Port-au-Prince',
                'departement': 'Ouest',
                'telephone': '+509 2813-1111',
                'latitude': 18.5463,
                'longitude': -72.3388,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 100,
            },
            {
                'nom': 'Hôpital Universitaire de la Paix',
                'type': 'public',
                'adresse': 'Delmas 33',
                'commune': 'Port-au-Prince',
                'departement': 'Ouest',
                'telephone': '+509 2813-2222',
                'latitude': 18.5604,
                'longitude': -72.3151,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 80,
            },
            {
                'nom': 'Centre de Transfusion Sanguine National',
                'type': 'public',
                'adresse': 'Rue Capois',
                'commune': 'Port-au-Prince',
                'departement': 'Ouest',
                'telephone': '+509 2813-3333',
                'latitude': 18.5439,
                'longitude': -72.3364,
                'horaires': 'Lun-Ven 8h-17h, Sam 8h-12h',
                'capacite_journaliere': 150,
            },
            {
                'nom': 'Hôpital Bernard Mevs',
                'type': 'prive',
                'adresse': 'Route de Delmas',
                'commune': 'Port-au-Prince',
                'departement': 'Ouest',
                'telephone': '+509 2813-4444',
                'latitude': 18.5678,
                'longitude': -72.3012,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 60,
            },
            {
                'nom': 'Hôpital Sacré-Cœur de Milot',
                'type': 'prive',
                'adresse': 'Milot',
                'commune': 'Milot',
                'departement': 'Nord',
                'telephone': '+509 2813-5555',
                'latitude': 19.6089,
                'longitude': -72.2151,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 50,
            },
            {
                'nom': 'Hôpital Justinien',
                'type': 'public',
                'adresse': 'Cap-Haïtien',
                'commune': 'Cap-Haïtien',
                'departement': 'Nord',
                'telephone': '+509 2813-6666',
                'latitude': 19.7572,
                'longitude': -72.2014,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 90,
            },
            {
                'nom': 'Hôpital Saint-Antoine de Jérémie',
                'type': 'prive',
                'adresse': 'Jérémie',
                'commune': 'Jérémie',
                'departement': 'Grand\'Anse',
                'telephone': '+509 2813-7777',
                'latitude': 18.6467,
                'longitude': -74.1167,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 40,
            },
            {
                'nom': 'Hôpital Sainte-Thérèse de Hinche',
                'type': 'public',
                'adresse': 'Hinche',
                'commune': 'Hinche',
                'departement': 'Centre',
                'telephone': '+509 2813-8888',
                'latitude': 19.1500,
                'longitude': -72.0167,
                'horaires': 'Lun-Ven 8h-16h',
                'capacite_journaliere': 30,
            },
            {
                'nom': 'Hôpital Notre-Dame de la Nativité',
                'type': 'ong',
                'adresse': 'Les Cayes',
                'commune': 'Les Cayes',
                'departement': 'Sud',
                'telephone': '+509 2813-9999',
                'latitude': 18.2000,
                'longitude': -73.7500,
                'horaires': '24h/24, 7j/7',
                'capacite_journaliere': 70,
            },
            {
                'nom': 'Croix-Rouge Haïtienne - Centre de Transfusion',
                'type': 'ong',
                'adresse': 'Rue Ducoste',
                'commune': 'Port-au-Prince',
                'departement': 'Ouest',
                'telephone': '+509 2813-0000',
                'latitude': 18.5480,
                'longitude': -72.3320,
                'horaires': 'Lun-Sam 7h-18h',
                'capacite_journaliere': 120,
            },
        ]
        
        groupes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        import random
        
        created_count = 0
        for data in centres_data:
            centre, created = Centre.objects.get_or_create(
                nom=data['nom'],
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Centre créé : {centre.nom}')
                )
                
                # Créer les stocks pour ce centre
                for groupe in groupes:
                    Stock.objects.get_or_create(
                        centre=centre,
                        groupe_sanguin=groupe,
                        defaults={
                            'quantite_disponible': random.randint(0, 50),
                            'seuil_alerte': 5,
                        }
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Centre déjà existant : {centre.nom}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {created_count} centres créés avec succès !')
        )