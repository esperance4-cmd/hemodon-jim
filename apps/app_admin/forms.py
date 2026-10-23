from django import forms
from apps.authentification.models import User
from apps.centres.models import Centre
from apps.stocks.models import Stock
from apps.demandes.models import Demande
from .models import Notification


# ============================================
# FORMULAIRES ADMIN
# ============================================

class UserAdminForm(forms.ModelForm):
    """Formulaire pour modifier un utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'telephone', 'groupe', 'adresse', 
            'commune', 'departement', 'date_naissance', 'groupe_sanguin', 
            'est_eligible', 'is_active', 'is_staff', 'is_superuser'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }


class CentreAdminForm(forms.ModelForm):
    """Formulaire d'édition centre pour l'admin"""
    
    class Meta:
        model = Centre
        fields = ['nom', 'type', 'adresse', 'commune', 'departement', 
                  'telephone', 'email', 'latitude', 'longitude', 
                  'capacite_journaliere', 'horaires', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'capacite_journaliere': forms.NumberInput(attrs={'class': 'form-control'}),
            'horaires': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockAdminForm(forms.ModelForm):
    """Formulaire de mise à jour des stocks"""
    
    class Meta:
        model = Stock
        fields = ['quantite_disponible', 'seuil_alerte']
        widgets = {
            'quantite_disponible': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class DemandeAdminForm(forms.ModelForm):
    """Formulaire de traitement des demandes"""
    
    class Meta:
        model = Demande
        fields = ['statut', 'urgence', 'notes']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'urgence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class NotificationForm(forms.ModelForm):
    """Formulaire de création de notification"""
    
    class Meta:
        model = Notification
        fields = ['titre', 'message', 'type', 'pour_tous', 'utilisateurs', 'lien']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la notification'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Contenu du message...'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'pour_tous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'utilisateurs': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'lien': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        labels = {
            'titre': 'Titre',
            'message': 'Message',
            'type': 'Type de notification',
            'pour_tous': 'Envoyer à tous les utilisateurs',
            'utilisateurs': 'Utilisateurs spécifiques (si non envoyé à tous)',
            'lien': 'Lien (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateurs'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['utilisateurs'].help_text = "Maintenez Ctrl pour sélectionner plusieurs utilisateurs"
    
    def clean(self):
        cleaned_data = super().clean()
        pour_tous = cleaned_data.get('pour_tous')
        utilisateurs = cleaned_data.get('utilisateurs')
        
        if not pour_tous and not utilisateurs:
            raise forms.ValidationError("Veuillez sélectionner au moins un utilisateur ou cocher 'Envoyer à tous'.")
        
        return cleaned_data


class NotificationFilterForm(forms.Form):
    """Formulaire de filtrage des notifications"""
    
    type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + list(Notification.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    lu = forms.ChoiceField(
        choices=[('', 'Toutes'), ('true', 'Lues'), ('false', 'Non lues')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )