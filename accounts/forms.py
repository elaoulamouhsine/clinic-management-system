from django import forms
from .models import User, Patient
from dossiers.models import Mutuelle

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe temporaire",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123456'}),
        help_text="Donnez ce mot de passe au patient."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': "Nom d'utilisateur (Login)",
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Email (Optionnel)"
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': '',
        }

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['cin', 'date_naissance', 'adresse', 'mutuelle']
        widgets = {
            'cin': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'mutuelle': forms.Select(attrs={'class': 'form-select'}),
        }