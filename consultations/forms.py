from django import forms
from .models import Consultation, Acte

class ConsultationForm(forms.ModelForm):
    actes = forms.ModelMultipleChoiceField(
        queryset=Acte.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Actes réalisés"
    )

    traitement_ordonnance = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Doliprane 1000mg...'}),
        required=False,
        label="Prescription (Ordonnance)",
        help_text="Laissez vide si aucune ordonnance n'est nécessaire."
    )

    class Meta:
        model = Consultation
        fields = ['diagnostic', 'commentaires', 'actes']
        widgets = {
            'diagnostic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
