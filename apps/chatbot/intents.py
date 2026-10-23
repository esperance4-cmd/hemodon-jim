"""
Module de gestion des intents pour le chatbot
Définit les intentions et les réponses du chatbot
"""

import random
import re

# ========== DÉFINITION DES INTENTS ==========
INTENTS = {
    'greeting': {
        'patterns': ['bonjour', 'salut', 'coucou', 'hello', 'hi', 'hey', 'bonsoir', 'bon matin', 'slt'],
        'responses': [
            "Bonjour ! 👋 Je suis votre assistant pour le don de sang. Comment puis-je vous aider ?",
            "Salut ! Je suis là pour vous guider dans votre parcours de don de sang. Posez-moi vos questions !",
            "Bonjour ! Que puis-je faire pour vous aujourd'hui concernant le don de sang ?",
            "Hey ! 😊 Je suis votre assistant HEMODON-JIM. Comment puis-je vous aider ?"
        ]
    },
    
    'donation_process': {
        'patterns': ['donner sang', 'comment donner', 'processus don', 'étapes don', 'faire un don', 'procédure don', 'comment ça se passe'],
        'responses': [
            "🩸 Le processus de don de sang comprend plusieurs étapes :\n\n"
            "1️⃣ Inscription et vérification de l'identité\n"
            "2️⃣ Questionnaire médical et entretien confidentiel\n"
            "3️⃣ Examen clinique (pouls, tension artérielle, taux d'hémoglobine)\n"
            "4️⃣ Prélèvement (environ 8 à 10 minutes)\n"
            "5️⃣ Collation et repos (15 minutes)\n\n"
            "L'ensemble dure environ 45 minutes. Souhaitez-vous plus de détails sur une étape spécifique ?"
        ]
    },
    
    'blood_groups': {
        'patterns': ['groupe sanguin', 'compatibilité', 'groupes compatibles', 'groupe sanguin compatible', 'rhésus', 'types de sang'],
        'responses': [
            "🩹 Les groupes sanguins sont classés en 4 types principaux :\n\n"
            "• A, B, AB et O avec Rhésus + ou -\n"
            "• Le donneur universel est O- (peut donner à tous)\n"
            "• Le receveur universel est AB+ (peut recevoir de tous)\n\n"
            "🔴 Groupes compatibles pour les transfusions :\n"
            "• O- → O+, A+, B+, AB+\n"
            "• O+ → O+, A+, B+, AB+\n"
            "• A- → A+, AB+\n"
            "• A+ → A+, AB+\n"
            "• B- → B+, AB+\n"
            "• B+ → B+, AB+\n"
            "• AB- → AB+\n"
            "• AB+ → AB+\n\n"
            "Quel groupe sanguin vous intéresse ?"
        ]
    },
    
    'eligibility': {
        'patterns': ['éligible', 'peux-je donner', 'conditions don', 'apte', 'qui peut donner', 'puis-je donner', 'conditions'],
        'responses': [
            "📋 Pour être éligible au don de sang, vous devez :\n\n"
            "✅ Être âgé de 18 à 70 ans\n"
            "✅ Peser plus de 50 kg\n"
            "✅ Être en bonne santé générale\n"
            "✅ Ne pas avoir de maladies transmissibles\n"
            "✅ Ne pas être enceinte ou allaiter\n"
            "✅ Ne pas avoir de tatouage ou piercing récent (<4 mois)\n"
            "✅ Ne pas avoir voyagé dans certaines zones à risque\n\n"
            "❌ Être à jeun (prendre un repas léger avant)\n\n"
            "Souhaitez-vous vérifier votre éligibilité personnelle ?"
        ]
    },
    
    'benefits': {
        'patterns': ['avantages don', 'bénéfices', 'pourquoi donner', 'importance don', 'utilité don', 'bienfaits'],
        'responses': [
            "❤️ Donner son sang est un acte généreux qui :\n\n"
            "🩸 Sauve jusqu'à 3 vies par don\n"
            "🔄 Permet de refaire son sang en 24h\n"
            "🏥 Soutient les hôpitaux et les patients\n"
            "📋 Offre un bilan de santé gratuit\n"
            "🙏 Apporte une grande satisfaction personnelle\n"
            "💰 C'est gratuit et anonyme\n\n"
            "En plus, c'est rapide, sécurisé et indolore ! 🩹"
        ]
    },
    
    'appointments': {
        'patterns': ['rendez-vous', 'prendre rendez-vous', 'planifier don', 'programmer don', 'réservation', 'rdv'],
        'responses': [
            "📅 Pour prendre un rendez-vous, vous pouvez :\n\n"
            "📱 Utiliser l'interface de réservation dans l'application\n"
            "🌐 Vous rendre sur notre site web\n"
            "📞 Appeler le 0 800 123 456 (appel gratuit)\n"
            "🏥 Vous rendre directement dans un centre de transfusion\n\n"
            "Souhaitez-vous que je vous guide pas à pas pour la réservation ?"
        ]
    },
    
    'faq': {
        'patterns': ['questions', 'faq', 'fréquentes', 'questions fréquentes', 'Q&A'],
        'responses': [
            "❓ Voici quelques questions fréquentes :\n\n"
            "❔ Est-ce que c'est douloureux ?\n"
            "➡ Non, comme une petite piqûre, très supportable.\n\n"
            "❔ Combien de temps dure un don ?\n"
            "➡ Environ 45 minutes (prélèvement + repos).\n\n"
            "❔ Puis-je donner si je suis sous traitement ?\n"
            "➡ Cela dépend, vérifiez avec un médecin avant.\n\n"
            "❔ À quelle fréquence puis-je donner ?\n"
            "➡ Tous les 3 mois pour les hommes, 4 mois pour les femmes.\n\n"
            "❔ Que dois-je manger avant ?\n"
            "➡ Un repas léger et boire beaucoup d'eau.\n\n"
            "Avez-vous d'autres questions ?"
        ]
    },
    
    'emergency': {
        'patterns': ['urgence', 'urgence sanguine', 'besoin urgent', 'manque sang', 'pénurie', 'alerte'],
        'responses': [
            "⚠️ EN CAS D'URGENCE SANGUINE :\n\n"
            "📞 Contactez immédiatement l'Établissement Français du Sang :\n"
            "   • 0 800 109 900 (appel gratuit)\n"
            "   • 24h/24, 7j/7\n\n"
            "🏥 Ou rendez-vous aux urgences de l'hôpital le plus proche\n"
            "🔴 Si vous êtes donneur compatible, vous serez contacté en priorité\n\n"
            "Souhaitez-vous que je vous aide à localiser un établissement ?"
        ]
    },
    
    'goodbye': {
        'patterns': ['au revoir', 'bye', 'à plus tard', 'merci au revoir', 'salut', 'adieu', 'à bientôt'],
        'responses': [
            "Merci pour votre intérêt pour le don de sang ! ❤️\n"
            "N'hésitez pas à revenir si vous avez d'autres questions. À bientôt !",
            "Au revoir et merci ! 🙏 Votre engagement sauve des vies. Prenez soin de vous.",
            "Bonne journée à vous ! 🌟 N'oubliez pas, chaque don compte."
        ]
    },
    
    'help': {
        'patterns': ['aide', 'help', 'que pouvez-vous faire', 'commandes', 'comment ça marche', 'fonctionnalités'],
        'responses': [
            "🤖 Je peux vous aider avec :\n\n"
            "🗣️ Répondre à vos questions sur le don de sang\n"
            "🩸 Vous informer sur les groupes sanguins et la compatibilité\n"
            "📋 Vous guider dans le processus de don\n"
            "📅 Vous aider à prendre un rendez-vous\n"
            "📍 Vous orienter vers les centres de don\n"
            "⚠️ Vous alerter en cas d'urgence\n\n"
            "Pour commencer, posez-moi une question !"
        ]
    },
    
    'center_location': {
        'patterns': ['centre don', 'où donner', 'localisation', 'point de don', 'adresse', 'près de chez moi'],
        'responses': [
            "📍 Je peux vous aider à trouver un centre de don près de chez vous !\n\n"
            "🔍 Utilisez notre outil de recherche avec votre code postal\n"
            "📍 Activez la géolocalisation pour trouver les centres proches\n"
            "🏥 Consultez la liste des centres partenaires dans l'application\n\n"
            "Souhaitez-vous rechercher maintenant ?"
        ]
    },
    
    'blood_shortage': {
        'patterns': ['pénurie sang', 'manque de sang', 'stock insuffisant', 'besoin sang', 'don urgent'],
        'responses': [
            "🔴 ALERTE PÉNURIE DE SANG :\n\n"
            "Actuellement, les groupes sanguins les plus sollicités sont :\n"
            "• O- (donneur universel)\n"
            "• A- et B-\n\n"
            "💪 Votre don peut faire la différence !\n"
            "📱 Consultez les besoins en temps réel dans l'application\n"
            "🏥 Contactez votre centre de transfusion le plus proche\n\n"
            "Souhaitez-vous voir les besoins actuels ?"
        ]
    },
    
    'thanks': {
        'patterns': ['merci', 'merci beaucoup', 'je vous remercie', 'cimer', 'thanks'],
        'responses': [
            "C'est un plaisir de vous aider ! 🙏 N'hésitez pas si vous avez d'autres questions.",
            "Je suis ravi de pouvoir vous assister ! 😊 À votre service.",
            "Merci à vous pour votre engagement dans le don de sang ! ❤️"
        ]
    }
}

# ========== FONCTIONS PRINCIPALES ==========

def get_intent(message):
    """
    Détermine l'intention à partir du message de l'utilisateur
    
    Args:
        message (str): Le message de l'utilisateur
    
    Returns:
        str: Le nom de l'intention détectée
    """
    message_lower = message.lower()
    
    # Vérifier chaque intent
    for intent_name, intent_data in INTENTS.items():
        if intent_name == 'default':
            continue
        patterns = intent_data.get('patterns', [])
        for pattern in patterns:
            # Recherche exacte ou partielle
            if pattern in message_lower or re.search(r'\b' + re.escape(pattern) + r'\b', message_lower):
                return intent_name
    
    # Si aucun intent n'est trouvé
    return 'default'


def get_response(intent_name):
    """
    Retourne une réponse pour l'intention donnée
    
    Args:
        intent_name (str): Le nom de l'intention
    
    Returns:
        str: Une réponse aléatoire pour cette intention
    """
    # Récupérer les données de l'intent
    intent_data = INTENTS.get(intent_name, INTENTS.get('default'))
    
    # Si l'intent n'existe pas, utiliser 'default'
    if not intent_data:
        intent_data = {
            'responses': [
                "Je ne suis pas sûr d'avoir bien compris. 🤔\n\n"
                "Je peux vous aider sur :\n"
                "• Le don de sang\n"
                "• Les groupes sanguins\n"
                "• Les rendez-vous\n"
                "• L'éligibilité\n"
                "• Les urgences\n\n"
                "Pouvez-vous reformuler votre question ?"
            ]
        }
    
    # Récupérer les réponses possibles
    responses = intent_data.get('responses', [
        "Je n'ai pas encore de réponse pour cela. Désolé ! 😅"
    ])
    
    # Choisir une réponse aléatoire
    return random.choice(responses)


def get_all_intents():
    """
    Retourne la liste de tous les intents disponibles
    
    Returns:
        list: Liste des noms d'intents
    """
    return list(INTENTS.keys())


def add_intent(name, patterns, responses):
    """
    Ajoute un nouvel intent dynamiquement
    
    Args:
        name (str): Nom de l'intent
        patterns (list): Liste des motifs de reconnaissance
        responses (list): Liste des réponses possibles
    """
    INTENTS[name] = {
        'patterns': patterns,
        'responses': responses
    }


def get_intent_examples():
    """
    Retourne des exemples de questions pour chaque intent
    
    Returns:
        dict: Dictionnaire avec les intents et leurs exemples
    """
    examples = {}
    for intent_name, intent_data in INTENTS.items():
        if intent_name != 'default':
            examples[intent_name] = intent_data.get('patterns', [])[:3]
    return examples


# ========== FONCTIONS SPÉCIFIQUES POUR LE DON DE SANG ==========

def get_compatible_groups(blood_group):
    """
    Retourne les groupes sanguins compatibles
    
    Args:
        blood_group (str): Le groupe sanguin
    
    Returns:
        dict: Compatibilités donneur/receveur
    """
    compat = {
        'O-': {
            'donne_a': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'recoit_de': ['O-']
        },
        'O+': {
            'donne_a': ['O+', 'A+', 'B+', 'AB+'],
            'recoit_de': ['O-', 'O+']
        },
        'A-': {
            'donne_a': ['A-', 'A+', 'AB-', 'AB+'],
            'recoit_de': ['O-', 'A-']
        },
        'A+': {
            'donne_a': ['A+', 'AB+'],
            'recoit_de': ['O-', 'O+', 'A-', 'A+']
        },
        'B-': {
            'donne_a': ['B-', 'B+', 'AB-', 'AB+'],
            'recoit_de': ['O-', 'B-']
        },
        'B+': {
            'donne_a': ['B+', 'AB+'],
            'recoit_de': ['O-', 'O+', 'B-', 'B+']
        },
        'AB-': {
            'donne_a': ['AB-', 'AB+'],
            'recoit_de': ['O-', 'A-', 'B-', 'AB-']
        },
        'AB+': {
            'donne_a': ['AB+'],
            'recoit_de': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
        }
    }
    return compat.get(blood_group.upper(), None)


def is_blood_compatible(donor_group, recipient_group):
    """
    Vérifie si un donneur est compatible avec un receveur
    
    Args:
        donor_group (str): Groupe du donneur
        recipient_group (str): Groupe du receveur
    
    Returns:
        bool: True si compatible
    """
    compat = get_compatible_groups(donor_group)
    if compat:
        return recipient_group.upper() in compat['donne_a']
    return False