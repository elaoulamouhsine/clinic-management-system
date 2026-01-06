from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import User
from .forms import UserRegistrationForm, PatientRegistrationForm
from django.contrib import messages  
from django.utils import timezone
from planning.models import RDV

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.DOCTEUR

    def handle_no_permission(self):
        messages.error(
            self.request, 
            "Accès Interdit : Vous avez tenté d'accéder à l'espace Docteur sans autorisation."
        )
        # 3. On redirige vers le dispatch (qui renverra vers le bon dashboard)
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
# 1. LA GARE DE TRIAGE (DISPATCHER)
# On utilise une View générique car il n'y a pas de template à afficher, juste une redirection logicielle.
class DispatchDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # [cite_start]Redirection basée sur les rôles définis dans le dictionnaire de données [cite: 32, 33, 35]
        if user.role == User.Role.DOCTEUR:
            return redirect('doctor_dashboard')
        elif user.role == User.Role.SECRETAIRE:
            return redirect('secretary_dashboard')
        elif user.role == User.Role.PATIENT:
            return redirect('patient_dashboard')
        elif user.role == User.Role.ADMIN:
            return redirect('/admin/')
            
        # Par défaut
        return redirect('login')

# 2. LES DASHBOARDS (TemplateView)
# TemplateView est parfait quand on veut juste afficher un HTML.

class DoctorDashboardView(LoginRequiredMixin, DoctorRequiredMixin, TemplateView):
    template_name = 'accounts/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        # Récupérer les RDV de CE médecin pour AUJOURD'HUI
        # Note : on utilise docteur__user pour faire le lien inverse
        rdvs_du_jour = RDV.objects.filter(
            docteur__user=user, 
            date=today
        ).order_by('heure')

        # Statistiques simples
        context['rdvs'] = rdvs_du_jour
        context['count_today'] = rdvs_du_jour.count()
        context['count_waiting'] = rdvs_du_jour.filter(statut='EN_ATTENTE').count()
        
        return context


# --- 2. DASHBOARD PATIENT ---
class PatientDashboardView(LoginRequiredMixin, PatientRequiredMixin, TemplateView):
    template_name = 'accounts/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # 1. Tous les RDV du patient (Passés et Futurs)
        mes_rdvs = RDV.objects.filter(patient__user=user).order_by('-date', '-heure')
        
        # 2. Le PROCHAIN RDV (Le premier qui est dans le futur ou aujourd'hui)
        prochain_rdv = mes_rdvs.filter(
            date__gte=today, 
            statut__in=['EN_ATTENTE', 'CONFIRME']
        ).order_by('date', 'heure').first()

        context['historique_rdvs'] = mes_rdvs
        context['prochain_rdv'] = prochain_rdv
        
        # Infos patient (simulées ici, à récupérer via user.patient si besoin)
        context['patient_info'] = user.patient_profile if hasattr(user, 'patient_profile') else None

        return context


# --- 3. DASHBOARD SECRÉTAIRE ---
class SecretaryDashboardView(LoginRequiredMixin, SecretaryRequiredMixin, TemplateView):
    template_name = 'accounts/secretary_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # La secrétaire voit TOUS les RDV de la clinique pour aujourd'hui
        context['rdvs_today'] = RDV.objects.filter(date=today).order_by('heure')
        context['total_rdv'] = context['rdvs_today'].count()
        
        return context
class HomeView(TemplateView):
    template_name = 'home.html'

class AddPatientView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'accounts/add_patient.html'

    # 1. Sécurité : Test pour vérifier si c'est une secrétaire
    def test_func(self):
        return self.request.user.role == User.Role.SECRETAIRE

    def handle_no_permission(self):
        # Redirection si l'utilisateur n'est pas secrétaire
        messages.error(self.request, "Accès réservé au secrétariat.")
        return redirect('dispatch_dashboard')

    # 2. Méthode GET : Affichage des formulaires vides
    def get(self, request, *args, **kwargs):
        context = {
            'user_form': UserRegistrationForm(),
            'patient_form': PatientRegistrationForm()
        }
        return render(request, self.template_name, context)

    # 3. Méthode POST : Traitement des données soumises
    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        patient_form = PatientRegistrationForm(request.POST)

        # On vérifie si les DEUX formulaires sont valides
        if user_form.is_valid() and patient_form.is_valid():
            
            # A. Création du User
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = User.Role.PATIENT
            user.save()

            # B. Création du Patient lié
            patient = patient_form.save(commit=False)
            patient.user = user # Lien crucial
            patient.save()

            messages.success(request, f"Dossier créé pour {user.last_name} {user.first_name}")
            return redirect('secretary_dashboard')
        
        # C. Si erreur : On réaffiche la page avec les erreurs (Django le fait auto grâce aux instances form)
        context = {
            'user_form': user_form,
            'patient_form': patient_form
        }
        return render(request, self.template_name, context)
    
class PatientHistoryView(LoginRequiredMixin, PatientRequiredMixin, ListView):
    model = RDV
    template_name = 'accounts/patient_history.html'
    context_object_name = 'rdvs'
    paginate_by = 10  # Affiche 10 RDV par page (gère la pagination auto)

    def get_queryset(self):
        # On filtre : Uniquement les RDV du patient connecté
        return RDV.objects.filter(
            patient__user=self.request.user
        ).order_by('-date', '-heure')