from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import RDV
from accounts.models import Patient, Docteur
from .forms import RDVRequestForm, RendezVousForm
from django.views import View
from django.shortcuts import render
from django.db.models import Q
import datetime

class RequestRDVView(LoginRequiredMixin, CreateView):
    model = RDV
    form_class = RDVRequestForm
    template_name = 'planning/request_rdv.html'
    success_url = reverse_lazy('patient_dashboard')

    def form_valid(self, form):
        # 1. Vérification avec le bon nom de relation (profile_patient)
        if not hasattr(self.request.user, 'profile_patient'):
            messages.error(self.request, "Erreur : Vous n'avez pas de dossier patient associé.")
            return redirect('patient_dashboard')

        # 2. On prépare l'objet
        rdv = form.save(commit=False)
        
        # 3. Assignation avec le bon attribut
        rdv.patient = self.request.user.profile_patient  # <--- CORRECTION ICI
        rdv.statut = 'EN_ATTENTE'
        
        # 4. Sauvegarde
        rdv.save()
        
        messages.success(self.request, "Votre demande de rendez-vous a été envoyée.")
        return redirect(self.success_url)

class RDVListView(LoginRequiredMixin, ListView):
    model = RDV
    template_name = 'planning/liste_rendez_vous.html'
    context_object_name = 'rdvs'

    def get_queryset(self):
        # On optimise les requêtes avec select_related pour aller chercher les infos 'user'
        queryset = RDV.objects.select_related('patient__user', 'docteur__user').all().order_by('-date', '-heure')
        
        date_filter = self.request.GET.get('date')
        patient_id = self.request.GET.get('patient')
        docteur_id = self.request.GET.get('docteur')
        search_query = self.request.GET.get('q') # Si vous voulez remettre la barre de recherche textuelle

        if date_filter:
            queryset = queryset.filter(date=date_filter)
        
        if patient_id:
            queryset = queryset.filter(patient__id=patient_id)

        if docteur_id:
            queryset = queryset.filter(docteur__id=docteur_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # CORRECTION ICI : On trie par user__last_name au lieu de nom
        context['tous_patients'] = Patient.objects.select_related('user').all().order_by('user__last_name')
        context['tous_docteurs'] = Docteur.objects.select_related('user').all().order_by('user__last_name')
        
        context['selected_date'] = self.request.GET.get('date', '')
        context['selected_patient'] = int(self.request.GET.get('patient')) if self.request.GET.get('patient') else ''
        context['selected_docteur'] = int(self.request.GET.get('docteur')) if self.request.GET.get('docteur') else ''
        
        return context

class RDVUpdateView(LoginRequiredMixin, UpdateView):
    model = RDV
    form_class = RendezVousForm  # Utilise le formulaire complet
    template_name = 'planning/form_rendez_vous.html' # On va créer ce fichier juste après
    success_url = reverse_lazy('liste_rendez_vous')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = "Modifier le Rendez-vous"
        return context

# 2. ACTIONS RAPIDES (Confirmer / Supprimer)
class RDVStatutView(LoginRequiredMixin, View):
    """
    Gère les actions rapides via bouton :
    - CONFIRME : Passe le statut à confirmé.
    - ANNULE : Supprime le rendez-vous de la BDD.
    """
    def post(self, request, pk, statut_code):
        rdv = get_object_or_404(RDV, pk=pk)
        
        if statut_code == 'ANNULE':
            # Option choisie : Suppression définitive
            rdv.delete()
            messages.warning(request, "Le rendez-vous a été annulé et supprimé.")
        
        elif statut_code == 'CONFIRME':
            rdv.statut = 'CONFIRME'
            rdv.save()
            messages.success(request, "Le rendez-vous a été confirmé.")
            
        return redirect('liste_rendez_vous')
