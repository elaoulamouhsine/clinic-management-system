from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
from accounts.models import Patient, User
from planning.models import RDV
from consultations.models import Consultation
from django.db.models import Q

from .models import Allergie, Maladie, Vaccin


class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Patient
    template_name = 'dossiers/patient_detail.html'
    context_object_name = 'patient'

    def test_func(self):
        dossier_visé = self.get_object()
        user = self.request.user

        if user.role in [User.Role.DOCTEUR, User.Role.SECRETAIRE]:
            return True

        if user.role == User.Role.PATIENT:
            if hasattr(user, 'profile_patient'):
                return user.profile_patient.pk == dossier_visé.pk

        return False

    def handle_no_permission(self):
        """
        Gère le cas où l'accès est refusé.
        Au lieu d'une page d'erreur 403 moche, on redirige intelligemment.
        """
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(self.request, "Accès refusé : Vous ne pouvez pas consulter ce dossier médical.")

        if self.request.user.role == User.Role.PATIENT:
            return redirect('patient_dashboard')
        else:
            return redirect('dispatch_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        consultations = Consultation.objects.filter(
            rdv__patient=patient
        ).select_related(
            'rdv',
            'rdv__docteur__user',
            'ordonnance'
        ).order_by('-rdv__date')

        context['consultations'] = consultations
        context['vaccinations'] = patient.vaccinations.select_related('vaccin').order_by('-date_injection')
        context['allergies'] = patient.antecedents_allergies.select_related('allergie')
        context['maladies'] = patient.antecedents_maladies.select_related('maladie')

        context['historique_rdv'] = patient.rdvs_pris.select_related('docteur').order_by('-date', '-heure')

        today = timezone.now().date()
        born = patient.date_naissance
        context['age'] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

        return context


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'dossiers/liste_patients.html'
    context_object_name = 'patients'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('user__last_name')

        search_nom = self.request.GET.get('search_nom')
        search_allergie = self.request.GET.get('search_allergie')
        search_maladie = self.request.GET.get('search_maladie')
        search_vaccin = self.request.GET.get('search_vaccin')

        if search_nom:
            queryset = queryset.filter(
                Q(user__last_name__icontains=search_nom) |
                Q(user__first_name__icontains=search_nom)
            )

        if search_allergie:
            queryset = queryset.filter(antecedents_allergies__allergie__id=search_allergie)

        if search_maladie:
            queryset = queryset.filter(antecedents_maladies__maladie__id=search_maladie)

        if search_vaccin:
            queryset = queryset.filter(vaccinations__vaccin__id=search_vaccin)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_allergies'] = Allergie.objects.all().order_by('nom_alrg')
        context['all_maladies'] = Maladie.objects.all().order_by('nom_mal')
        context['all_vaccins'] = Vaccin.objects.all().order_by('nom_vac')

        context['current_search_nom'] = self.request.GET.get('search_nom', '')
        context['current_search_allergie'] = int(self.request.GET.get('search_allergie')) if self.request.GET.get('search_allergie') else ''
        context['current_search_maladie'] = int(self.request.GET.get('search_maladie')) if self.request.GET.get('search_maladie') else ''
        context['current_search_vaccin'] = int(self.request.GET.get('search_vaccin')) if self.request.GET.get('search_vaccin') else ''

        return context
