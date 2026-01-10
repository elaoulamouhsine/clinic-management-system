from django import forms
from django.utils import timezone
from .models import RDV

class RDVRequestForm(forms.ModelForm):
    class Meta:
        model = RDV
        fields = ['docteur', 'date', 'heure', 'motif']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Douleur au dos, Consultation de suivi...'}),
            'docteur': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'docteur': 'Médecin souhaité',
            'date': 'Date souhaitée',
            'heure': 'Heure préférée',
            'motif': 'Motif de la consultation'
        }

    # Validation personnalisée : Empêcher les dates passées
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise forms.ValidationError("Vous ne pouvez pas prendre rendez-vous dans le passé ")
        return date
    
class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RDV
        fields = ['patient', 'docteur', 'date', 'heure', 'motif', 'statut']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'docteur': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }