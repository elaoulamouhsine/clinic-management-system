# accounts/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import User

class PatientRequiredMixin(UserPassesTestMixin):
    """
    Vérifie que l'utilisateur est bien un PATIENT.
    Sinon, on le redirige vers le dispatch (qui le renverra au bon endroit).
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.PATIENT

    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé aux patients.")
        return redirect('dispatch_dashboard')

class SecretaryRequiredMixin(UserPassesTestMixin):
    """
    Vérifie que l'utilisateur est une SECRÉTAIRE.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.SECRETAIRE

    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé au secrétariat.")
        return redirect('dispatch_dashboard')