from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription"""
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Champs supplémentaires - à adapter selon votre modèle
    telephone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_naissance = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    adresse = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    ville = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pays = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    blood_group = forms.ChoiceField(
        choices=[('', '--- Sélectionnez ---')] + [(g, g) for g in ['A', 'B', 'AB', 'O']],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rh_factor = forms.ChoiceField(
        choices=[('', '--- Sélectionnez ---'), ('+', 'Rh+'), ('-', 'Rh-')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Utiliser GROUPE_CHOICES
    groupe = forms.ChoiceField(
        choices=User.GROUPE_CHOICES if hasattr(User, 'GROUPE_CHOICES') else [],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        is_admin = kwargs.pop('is_admin', False)
        super().__init__(*args, **kwargs)
        
        # Ajouter les champs supplémentaires s'ils existent dans le modèle
        user_fields = [f.name for f in User._meta.get_fields()]
        
        if 'telephone' not in user_fields:
            self.fields.pop('telephone', None)
        if 'date_naissance' not in user_fields:
            self.fields.pop('date_naissance', None)
        if 'adresse' not in user_fields:
            self.fields.pop('adresse', None)
        if 'ville' not in user_fields:
            self.fields.pop('ville', None)
        if 'pays' not in user_fields:
            self.fields.pop('pays', None)
        if 'blood_group' not in user_fields:
            self.fields.pop('blood_group', None)
        if 'rh_factor' not in user_fields:
            self.fields.pop('rh_factor', None)
        
        # Si l'utilisateur n'est pas admin, masquer le champ groupe
        if not is_admin:
            self.fields.pop('groupe', None)
        
        # Ajouter des classes aux champs
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Assigner les champs supplémentaires s'ils existent
        for field in ['telephone', 'date_naissance', 'adresse', 'ville', 'pays', 'blood_group', 'rh_factor']:
            if field in self.cleaned_data and hasattr(user, field):
                setattr(user, field, self.cleaned_data[field])
        
        if 'groupe' in self.cleaned_data and hasattr(user, 'groupe'):
            user.groupe = self.cleaned_data['groupe']
        
        if commit:
            user.save()
            # Créer le profil s'il n'existe pas
            Profile.objects.get_or_create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification du profil - adapté au modèle existant"""
    
    class Meta:
        model = User
        # Utiliser uniquement les champs qui existent vraiment
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter dynamiquement les champs qui existent dans le modèle
        user_fields = [f.name for f in User._meta.get_fields()]
        
        # Champs optionnels à ajouter s'ils existent
        optional_fields = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'rh_factor': forms.Select(attrs={'class': 'form-control'}),
        }
        
        for field_name, widget in optional_fields.items():
            if field_name in user_fields:
                self.fields[field_name] = forms.CharField(
                    required=False,
                    widget=widget,
                    label=field_name.replace('_', ' ').title()
                )
                # Ajouter des valeurs si elles existent
                if hasattr(self.instance, field_name):
                    self.initial[field_name] = getattr(self.instance, field_name)
        
        # Si blood_group existe, ajouter les choix
        if 'blood_group' in self.fields:
            self.fields['blood_group'].widget = forms.Select(
                choices=[('', '--- Sélectionnez ---')] + [(g, g) for g in ['A', 'B', 'AB', 'O']],
                attrs={'class': 'form-control'}
            )
        
        if 'rh_factor' in self.fields:
            self.fields['rh_factor'].widget = forms.Select(
                choices=[('', '--- Sélectionnez ---'), ('+', 'Rh+'), ('-', 'Rh-')],
                attrs={'class': 'form-control'}
            )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


class ProfileDetailForm(forms.ModelForm):
    """Formulaire détaillé du profil"""
    
    class Meta:
        model = Profile
        fields = ['bio', 'weight_kg', 'height_cm', 'medical_conditions', 'allergies', 
                  'medications', 'preferred_center', 'preferred_time', 
                  'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'preferred_center': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_time': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs optionnels
        for field in self.fields:
            self.fields[field].required = False


class UserRoleForm(forms.ModelForm):
    """Formulaire de modification du rôle"""
    
    class Meta:
        model = User
        fields = ['groupe'] if hasattr(User, 'groupe') else []
        widgets = {
            'groupe': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(User, 'GROUPE_CHOICES'):
            self.fields['groupe'].choices = User.GROUPE_CHOICES


class UserAdminForm(UserChangeForm):
    """Formulaire admin pour les utilisateurs"""
    
    password = None
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter les champs supplémentaires s'ils existent
        user_fields = [f.name for f in User._meta.get_fields()]
        
        optional_fields = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'groupe': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'rh_factor': forms.Select(attrs={'class': 'form-control'}),
        }
        
        for field_name, widget in optional_fields.items():
            if field_name in user_fields:
                self.fields[field_name] = forms.CharField(
                    required=False,
                    widget=widget,
                    label=field_name.replace('_', ' ').title()
                )
                if hasattr(self.instance, field_name):
                    self.initial[field_name] = getattr(self.instance, field_name)
        
        # Ajouter les choix pour les select
        if 'groupe' in self.fields and hasattr(User, 'GROUPE_CHOICES'):
            self.fields['groupe'].widget.choices = User.GROUPE_CHOICES
        
        if 'blood_group' in self.fields:
            self.fields['blood_group'].widget.choices = [('', '---')] + [(g, g) for g in ['A', 'B', 'AB', 'O']]
        
        if 'rh_factor' in self.fields:
            self.fields['rh_factor'].widget.choices = [('', '---'), ('+', 'Rh+'), ('-', 'Rh-')]