from django import forms
from .models import Consultation, Acte

class ConsultationForm(forms.ModelForm):
    # Champ pour sélectionner les actes (cases à cocher multiples)
    actes = forms.ModelMultipleChoiceField(
        queryset=Acte.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Actes réalisés"
    )

    # Champ "virtuel" pour l'ordonnance (n'existe pas dans Consultation, mais on le traitera dans la vue)
    traitement_ordonnance = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Doliprane 1000mg...'}),
        required=False,
        label="Prescription (Ordonnance)",
        help_text="Laissez vide si aucune ordonnance n'est nécessaire."
    )

    class Meta:
        model = Consultation
        fields = ['diagnostic', 'commentaires', 'actes'] # On exclut 'rdv' car il sera auto-assigné
        widgets = {
            'diagnostic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }