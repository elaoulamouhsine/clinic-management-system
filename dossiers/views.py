from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
# Import des modèles
from accounts.models import Patient, User
from planning.models import RDV
from consultations.models import Consultation
from django.db.models import Q
# Les modèles dossiers sont déjà liés via les related_name, pas besoin de les importer pour les requêtes

from .models import Allergie, Maladie, Vaccin
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
        consultations = Consultation.objects.filter(
            rdv__patient=patient
        ).select_related(
            'rdv', 
            'rdv__docteur__user', 
            'ordonnance'
        ).order_by('-rdv__date')

        context['consultations'] = consultations
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
class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'dossiers/liste_patients.html'
    context_object_name = 'patients'
    
    def get_queryset(self):
        # 1. On récupère tous les patients de base
        queryset = super().get_queryset().order_by('user__last_name')
        
        # 2. On récupère les paramètres GET (ce que l'utilisateur a tapé/choisi)
        search_nom = self.request.GET.get('search_nom')
        search_allergie = self.request.GET.get('search_allergie')
        search_maladie = self.request.GET.get('search_maladie')
        search_vaccin = self.request.GET.get('search_vaccin')

        # 3. Application des filtres si nécessaire
        
        # Filtre par Nom ou Prénom
        if search_nom:
            queryset = queryset.filter(
                Q(user__last_name__icontains=search_nom) | 
                Q(user__first_name__icontains=search_nom)
            )

        # Filtre par Allergie (via la table intermédiaire)
        if search_allergie:
            queryset = queryset.filter(antecedents_allergies__allergie__id=search_allergie)

        # Filtre par Maladie
        if search_maladie:
            queryset = queryset.filter(antecedents_maladies__maladie__id=search_maladie)

        # Filtre par Vaccin
        if search_vaccin:
            queryset = queryset.filter(vaccinations__vaccin__id=search_vaccin)
            
        return queryset.distinct() # .distinct() est important pour éviter les doublons après un join

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 4. On envoie les listes complètes pour remplir les <select> HTML
        context['all_allergies'] = Allergie.objects.all().order_by('nom_alrg')
        context['all_maladies'] = Maladie.objects.all().order_by('nom_mal')
        context['all_vaccins'] = Vaccin.objects.all().order_by('nom_vac')
        
        # On renvoie aussi les valeurs actuelles pour garder le select sélectionné après recherche
        context['current_search_nom'] = self.request.GET.get('search_nom', '')
        context['current_search_allergie'] = int(self.request.GET.get('search_allergie')) if self.request.GET.get('search_allergie') else ''
        context['current_search_maladie'] = int(self.request.GET.get('search_maladie')) if self.request.GET.get('search_maladie') else ''
        context['current_search_vaccin'] = int(self.request.GET.get('search_vaccin')) if self.request.GET.get('search_vaccin') else ''
        
        return context