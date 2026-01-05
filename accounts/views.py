from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import User
from django.contrib import messages  


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
    # Chemin relatif depuis le dossier global 'templates/'
    template_name = 'accounts/doctor_dashboard.html'

class SecretaryDashboardView(LoginRequiredMixin, SecretaryRequiredMixin, TemplateView):
    template_name = 'accounts/secretary_dashboard.html'

class PatientDashboardView(LoginRequiredMixin,PatientRequiredMixin, TemplateView):
    template_name = 'accounts/patient_dashboard.html'
class HomeView(TemplateView):
    template_name = 'home.html'