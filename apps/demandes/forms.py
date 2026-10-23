from django import forms
from django.utils import timezone
from .models import Demande
from apps.centres.models import Centre


class DemandeCreateForm(forms.ModelForm):
    """Formulaire de création d'une demande de sang"""
    
    class Meta:
        model = Demande
        fields = ['groupe_sanguin', 'quantite_necessaire', 'centre_destination', 'urgence', 'notes']
        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'quantite_necessaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'centre_destination': forms.Select(attrs={'class': 'form-select'}),
            'urgence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Informations complémentaires...'}),
        }
        labels = {
            'groupe_sanguin': 'Groupe sanguin nécessaire',
            'quantite_necessaire': 'Nombre de poches nécessaires',
            'centre_destination': 'Centre de destination',
            'urgence': 'Demande urgente',
            'notes': 'Observations',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les centres actifs
        self.fields['centre_destination'].queryset = Centre.objects.filter(est_actif=True)
        
        # Si l'utilisateur est un personnel hospitalier, pré-remplir le centre
        if user and hasattr(user, 'groupe') and user.groupe == 'hospitalier':
            # Vous pouvez ajouter une logique pour pré-remplir le centre
            pass
    
    def clean_quantite_necessaire(self):
        quantite = self.cleaned_data.get('quantite_necessaire')
        if quantite < 1:
            raise forms.ValidationError("La quantité doit être d'au moins 1 poche.")
        if quantite > 50:
            raise forms.ValidationError("La quantité ne peut pas dépasser 50 poches.")
        return quantite


class DemandeUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour d'une demande (admin)"""
    
    class Meta:
        model = Demande
        fields = ['statut', 'urgence', 'notes']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'urgence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'statut': 'Statut de la demande',
            'urgence': 'Marquer comme urgente',
            'notes': 'Notes de traitement',
        }


class DemandeFilterForm(forms.Form):
    """Formulaire de filtrage des demandes"""
    
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + list(Demande.STATUT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    urgence = forms.ChoiceField(
        choices=[('', 'Toutes'), ('true', 'Urgentes'), ('false', 'Non urgentes')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    groupe_sanguin = forms.ChoiceField(
        choices=[('', 'Tous les groupes')] + list(Demande.GROUPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par ID, demandeur, centre...'
        })
    )