from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import User
from .forms import UserRegistrationForm, PatientRegistrationForm
from django.contrib import messages
from django.utils import timezone
from planning.models import RDV
from consultations.models import Consultation
from facturation.models import Facture
from django.db.models import Sum


class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.DOCTEUR

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Accès Interdit : Vous avez tenté d'accéder à l'espace Docteur sans autorisation."
        )
        return redirect('dispatch_dashboard')


class SecretaryRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.SECRETAIRE

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Accès Interdit : Cette page est réservée au personnel administratif."
        )
        return redirect('dispatch_dashboard')


class PatientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.PATIENT

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Accès Interdit : Vous ne pouvez pas accéder à l'espace Patient."
        )
        return redirect('dispatch_dashboard')


class DispatchDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.role == User.Role.DOCTEUR:
            return redirect('doctor_dashboard')
        elif user.role == User.Role.SECRETAIRE:
            return redirect('secretary_dashboard')
        elif user.role == User.Role.PATIENT:
            return redirect('patient_dashboard')
        elif user.role == User.Role.ADMIN:
            return redirect('/admin/')

        return redirect('login')


class DoctorDashboardView(LoginRequiredMixin, DoctorRequiredMixin, TemplateView):
    template_name = 'accounts/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        rdvs_du_jour = RDV.objects.filter(
            docteur__user=user,
            date=today,
            statut__in=['CONFIRME', 'EN_ATTENTE']
        ).order_by('heure')

        revenu = Facture.objects.filter(
            consultation__rdv__docteur__user=user,
            consultation__rdv__date=today
        ).aggregate(Sum('montant'))['montant__sum']

        context['rdvs_du_jour'] = rdvs_du_jour
        context['count_today'] = RDV.objects.filter(docteur__user=user, date=today).count()
        context['count_waiting'] = rdvs_du_jour.count()
        context['revenu_jour'] = revenu if revenu else 0

        return context


class PatientDashboardView(LoginRequiredMixin, PatientRequiredMixin, TemplateView):
    template_name = 'accounts/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        rdvs_futurs = RDV.objects.filter(
            patient__user=user,
            statut__in=['EN_ATTENTE', 'CONFIRME']
        ).order_by('date', 'heure')

        consultations = Consultation.objects.filter(
            rdv__patient__user=user
        ).select_related(
            'rdv',
            'rdv__docteur',
            'rdv__docteur__user',
            'ordonnance'
        ).order_by('-rdv__date')

        mes_factures = Facture.objects.filter(
            consultation__rdv__patient__user=user
        ).order_by('-date_facture')

        context['mes_factures'] = mes_factures
        context['rdvs_futurs'] = rdvs_futurs
        context['consultations'] = consultations

        if hasattr(user, 'profile_patient'):
            context['patient_info'] = user.profile_patient

        return context


class SecretaryDashboardView(LoginRequiredMixin, SecretaryRequiredMixin, TemplateView):
    template_name = 'accounts/secretary_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        context['rdvs_today'] = RDV.objects.filter(date=today).order_by('heure')
        context['total_rdv'] = context['rdvs_today'].count()

        return context


class HomeView(TemplateView):
    template_name = 'home.html'


class AddPatientView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'accounts/add_patient.html'

    def test_func(self):
        return self.request.user.role == User.Role.SECRETAIRE

    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé au secrétariat.")
        return redirect('dispatch_dashboard')

    def get(self, request, *args, **kwargs):
        context = {
            'user_form': UserRegistrationForm(),
            'patient_form': PatientRegistrationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        patient_form = PatientRegistrationForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():

            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = User.Role.PATIENT
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()

            messages.success(request, f"Dossier créé pour {user.last_name} {user.first_name}")
            return redirect('secretary_dashboard')

        context = {
            'user_form': user_form,
            'patient_form': patient_form
        }
        return render(request, self.template_name, context)


class PatientHistoryView(LoginRequiredMixin, PatientRequiredMixin, ListView):
    model = RDV
    template_name = 'accounts/patient_history.html'
    context_object_name = 'rdvs'
    paginate_by = 10

    def get_queryset(self):
        return RDV.objects.filter(
            patient__user=self.request.user
        ).order_by('-date', '-heure')
