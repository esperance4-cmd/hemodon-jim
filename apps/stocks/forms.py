from django import forms
from .models import Stock
from apps.centres.models import Centre


class StockUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour d'un stock"""
    
    class Meta:
        model = Stock
        fields = ['quantite_disponible', 'seuil_alerte']
        widgets = {
            'quantite_disponible': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
            'seuil_alerte': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
        }
    
    def clean_quantite_disponible(self):
        quantite = self.cleaned_data.get('quantite_disponible')
        if quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return quantite


class StockBulkUpdateForm(forms.Form):
    """Formulaire de mise à jour groupée des stocks"""
    
    centre = forms.ModelChoiceField(
        queryset=Centre.objects.filter(est_actif=True),
        empty_label="Sélectionnez un centre",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    groupe_sanguin = forms.ChoiceField(
        choices=[('', 'Sélectionnez un groupe')] + list(Stock.GROUPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantite = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class StockFilterForm(forms.Form):
    """Formulaire de filtrage des stocks"""
    
    centre = forms.ModelChoiceField(
        queryset=Centre.objects.filter(est_actif=True),
        empty_label="Tous les centres",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    groupe_sanguin = forms.ChoiceField(
        choices=[('', 'Tous les groupes')] + list(Stock.GROUPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    alerte = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un centre...'
        })
    )