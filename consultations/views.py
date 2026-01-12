from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from planning.models import RDV
from .models import Consultation, Ordonnance
from facturation.models import Facture
from .forms import ConsultationForm

class ConsultationCreateView(LoginRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'consultations/form_consultation.html'

    def get_context_data(self, **kwargs):
        """Passe le RDV au template pour afficher les infos du patient"""
        context = super().get_context_data(**kwargs)
        rdv_id = self.kwargs.get('rdv_id')
        context['rdv'] = get_object_or_404(RDV, id=rdv_id)
        return context

    def form_valid(self, form):
        rdv_id = self.kwargs.get('rdv_id')
        rdv = get_object_or_404(RDV, id=rdv_id)

        # Vérification de sécurité : Le RDV doit appartenir au médecin connecté
        if rdv.docteur.user != self.request.user:
            messages.error(self.request, "Vous ne pouvez pas traiter ce rendez-vous.")
            return redirect('doctor_dashboard')

        # TRANSACTION ATOMIQUE : Tout réussit ou tout échoue
        with transaction.atomic():
            # 1. Sauvegarde de la Consultation
            consultation = form.save(commit=False)
            consultation.rdv = rdv
            consultation.save()
            
            # Sauvegarde des ManyToMany (Actes) après avoir l'ID
            form.save_m2m() 

            # 2. Gestion de l'Ordonnance (si le champ est rempli)
            traitement = form.cleaned_data.get('traitement_ordonnance')
            if traitement:
                Ordonnance.objects.create(
                    consultation=consultation,
                    traitement=traitement
                )

            # 3. Génération automatique de la Facture
            # On la crée vide, la méthode save() du modèle calculera le montant
            # basé sur les actes qu'on vient de lier.
            Facture.objects.create(
                consultation=consultation,
                statut_paiement='NON_PAYE'
            )

            # 4. Mise à jour du statut du RDV
            rdv.statut = 'TERMINE'
            rdv.save()

        messages.success(self.request, "Consultation enregistrée avec succès.")
        return redirect('doctor_dashboard')