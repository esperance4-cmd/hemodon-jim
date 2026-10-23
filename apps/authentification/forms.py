# apps/authentification/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=True)
    groupe_sanguin = forms.ChoiceField(
        choices=[('', 'Sélectionnez votre groupe sanguin')] + list(User.GROUPE_SANGUIN_CHOICES),
        required=False
    )
    adresse = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    commune = forms.CharField(required=False)
    departement = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'telephone', 'password1', 'password2', 
                  'groupe_sanguin', 'adresse', 'commune', 'departement')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telephone = self.cleaned_data['telephone']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """Formulaire pour modifier le profil"""
    class Meta:
        model = User
        fields = ['email', 'telephone', 'adresse', 'commune', 'departement', 
                  'date_naissance', 'groupe_sanguin', 'photo']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }