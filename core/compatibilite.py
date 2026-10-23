"""
Module de compatibilité des groupes sanguins pour le système de don de sang.
"""

def groupes_compatibles_pour_receveur(groupe_sanguin):
    """
    Retourne la liste des groupes sanguins compatibles pour un receveur.
    
    Args:
        groupe_sanguin (str): Le groupe sanguin du receveur (ex: 'A+', 'O-', etc.)
    
    Returns:
        list: Liste des groupes sanguins compatibles pour la transfusion
    """
    compatibilite = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    }
    return compatibilite.get(groupe_sanguin.upper(), [])


def groupes_compatibles_pour_donneur(groupe_sanguin):
    """
    Retourne la liste des groupes sanguins compatibles pour un donneur.
    
    Args:
        groupe_sanguin (str): Le groupe sanguin du donneur (ex: 'A+', 'O-', etc.)
    
    Returns:
        list: Liste des groupes sanguins qui peuvent recevoir ce sang
    """
    compatibilite = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    return compatibilite.get(groupe_sanguin.upper(), [])


def est_compatible(groupe_donneur, groupe_receveur):
    """
    Vérifie si un donneur est compatible avec un receveur.
    
    Args:
        groupe_donneur (str): Groupe sanguin du donneur
        groupe_receveur (str): Groupe sanguin du receveur
    
    Returns:
        bool: True si compatible, False sinon
    """
    groupes_compatibles = groupes_compatibles_pour_receveur(groupe_receveur)
    return groupe_donneur.upper() in groupes_compatibles


def groupes_universels():
    """
    Retourne les groupes sanguins universels.
    
    Returns:
        dict: Dictionnaire avec les donneurs et receveurs universels
    """
    return {
        'donneur_universel': 'O-',
        'receveur_universel': 'AB+'
    }


def compatibilite_croisee(groupe1, groupe2):
    """
    Calcule la compatibilité croisée entre deux groupes sanguins.
    
    Args:
        groupe1 (str): Premier groupe sanguin
        groupe2 (str): Deuxième groupe sanguin
    
    Returns:
        dict: Dictionnaire avec les compatibilités dans les deux sens
    """
    return {
        f'{groupe1} -> {groupe2}': est_compatible(groupe1, groupe2),
        f'{groupe2} -> {groupe1}': est_compatible(groupe2, groupe1)
    }


def groupes_par_rhésus(rhésus='+'):
    """
    Retourne les groupes sanguins par type de rhésus.
    
    Args:
        rhésus (str): '+' ou '-'
    
    Returns:
        list: Liste des groupes sanguins avec le rhésus spécifié
    """
    tous_les_groupes = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
    return [g for g in tous_les_groupes if g.endswith(rhésus)]


# Constantes pour les groupes sanguins
GROUPES_SANGUINS = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']

# Règles de compatibilité simplifiées (pour référence)
REGLES_COMPATIBILITE = {
    'O-': {'donne_a': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'], 'recoit_de': ['O-']},
    'O+': {'donne_a': ['O+', 'A+', 'B+', 'AB+'], 'recroit_de': ['O-', 'O+']},
    'A-': {'donne_a': ['A-', 'A+', 'AB-', 'AB+'], 'recroit_de': ['O-', 'A-']},
    'A+': {'donne_a': ['A+', 'AB+'], 'recroit_de': ['O-', 'O+', 'A-', 'A+']},
    'B-': {'donne_a': ['B-', 'B+', 'AB-', 'AB+'], 'recroit_de': ['O-', 'B-']},
    'B+': {'donne_a': ['B+', 'AB+'], 'recroit_de': ['O-', 'O+', 'B-', 'B+']},
    'AB-': {'donne_a': ['AB-', 'AB+'], 'recroit_de': ['O-', 'A-', 'B-', 'AB-']},
    'AB+': {'donne_a': ['AB+'], 'recroit_de': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']},
}