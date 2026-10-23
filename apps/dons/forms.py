from django import forms
from django.utils import timezone
from .models import Don
from apps.centres.models import Centre

class DonCreateForm(forms.ModelForm):
    """Formulaire de planification d'un don"""
    
    class Meta:
        model = Don
        fields = ['centre', 'date_planifiee', 'observations']
        widgets = {
            'date_planifiee': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'observations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['centre'].queryset = Centre.objects.filter(est_actif=True)
        self.fields['centre'].widget.attrs.update({'class': 'form-select'})
        self.fields['date_planifiee'].widget.attrs.update({'class': 'form-control'})
    
    def clean_date_planifiee(self):
        """Vérifie que la date est dans le futur"""
        date = self.cleaned_data.get('date_planifiee')
        if date and date < timezone.now():
            raise forms.ValidationError("La date doit être dans le futur.")
        return date


class DonUpdateForm(forms.ModelForm):
    """Formulaire de modification d'un don (admin)"""
    
    class Meta:
        model = Don
        fields = ['centre', 'date_planifiee', 'statut', 'observations']
        widgets = {
            'date_planifiee': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'observations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['centre'].queryset = Centre.objects.filter(est_actif=True)
        self.fields['centre'].widget.attrs.update({'class': 'form-select'})
        self.fields['date_planifiee'].widget.attrs.update({'class': 'form-control'})
        self.fields['statut'].widget.attrs.update({'class': 'form-select'})