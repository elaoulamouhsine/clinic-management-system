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

        if rdv.docteur.user != self.request.user:
            messages.error(self.request, "Vous ne pouvez pas traiter ce rendez-vous.")
            return redirect('doctor_dashboard')

        with transaction.atomic():
            consultation = form.save(commit=False)
            consultation.rdv = rdv
            consultation.save()

            form.save_m2m()

            traitement = form.cleaned_data.get('traitement_ordonnance')
            if traitement:
                Ordonnance.objects.create(
                    consultation=consultation,
                    traitement=traitement
                )

            Facture.objects.create(
                consultation=consultation,
                statut_paiement='NON_PAYE'
            )

            rdv.statut = 'TERMINE'
            rdv.save()

        messages.success(self.request, "Consultation enregistrée avec succès.")
        return redirect('doctor_dashboard')
