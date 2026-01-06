from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
# Import des modèles
from accounts.models import Patient, User
from planning.models import RDV
# Les modèles dossiers sont déjà liés via les related_name, pas besoin de les importer pour les requêtes

class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Patient
    template_name = 'dossiers/patient_detail.html'
    context_object_name = 'patient'

# --- SÉCURITÉ (C'est ici que tout se joue) ---
    def test_func(self):
        # 1. On récupère le dossier que l'utilisateur essaie de voir
        dossier_visé = self.get_object() 
        user = self.request.user

        # Règle 1 : Le personnel médical (Docteur/Secrétaire) a accès à tout
        if user.role in [User.Role.DOCTEUR, User.Role.SECRETAIRE]:
            return True

        # Règle 2 : Le Patient ne peut voir QUE son propre dossier
        if user.role == User.Role.PATIENT:
            # On vérifie si le patient connecté est bien le propriétaire du dossier visé
            # On utilise .pk pour comparer les ID
            if hasattr(user, 'profile_patient'): # Ou user.patient selon votre related_name
                 # Attention: Adaptez 'patient_profile' selon votre related_name (probablement 'patient' ou 'patient_profile')
                 # Si vous n'avez pas mis de related_name, c'est 'patient'
                 return user.profile_patient.pk == dossier_visé.pk
            
        return False

    def handle_no_permission(self):
        """
        Gère le cas où l'accès est refusé.
        Au lieu d'une page d'erreur 403 moche, on redirige intelligemment.
        """
        # Si l'utilisateur n'est pas connecté, comportement standard (vers login)
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
            
        # Si l'utilisateur est connecté mais tente de tricher :
        messages.error(self.request, "Accès refusé : Vous ne pouvez pas consulter ce dossier médical.")
        
        # On le renvoie vers son propre dashboard
        if self.request.user.role == User.Role.PATIENT:
            return redirect('patient_dashboard') # Assurez-vous que c'est le bon nom d'URL
        else:
            return redirect('dispatch_dashboard')

    # --- FIN SÉCURITÉ ---

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object # L'objet patient récupéré par l'URL (pk)

        # 1. Récupération des données médicales via les "related_name" définis dans vos models
        # Ces noms viennent de votre fichier dossiers/models.py
        context['vaccinations'] = patient.vaccinations.select_related('vaccin').order_by('-date_injection')
        context['allergies'] = patient.antecedents_allergies.select_related('allergie')
        context['maladies'] = patient.antecedents_maladies.select_related('maladie')

        # 2. Récupération de l'historique des RDV (App Planning)
        context['historique_rdv'] = patient.rdvs_pris.select_related('docteur').order_by('-date', '-heure')
        
        # 3. Calcul de l'âge (Bonus pratique)
        today = timezone.now().date()
        born = patient.date_naissance
        context['age'] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

        return context