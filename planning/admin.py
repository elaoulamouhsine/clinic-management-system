from django.contrib import admin
from django.utils.html import format_html 
from .models import RDV

@admin.register(RDV)
class RDVAdmin(admin.ModelAdmin):
    # 1. Colonnes à afficher dans la liste
    list_display = ('date', 'heure', 'get_patient', 'get_docteur', 'get_statut_colored')
    
    # 2. Filtres sur la droite (Indispensable pour une secrétaire)
    list_filter = ('statut', 'date', 'docteur')
    
    # 3. Barre de recherche (Chercher par nom patient, CIN ou nom docteur)
    search_fields = (
        'patient__user__last_name', 
        'patient__user__first_name', 
        'patient__cin',
        'docteur__user__last_name'
    )

    # 4. Navigation par date (Ajoute une barre en haut pour naviguer par année/mois/jour)
    date_hierarchy = 'date'
    
    # 5. Ordre par défaut (Du plus récent au plus ancien)
    ordering = ['-date', '-heure']

    # --- MÉTHODES PERSONNALISÉES ---

    @admin.display(description='Patient', ordering='patient__user__last_name')
    def get_patient(self, obj):
        return f"{obj.patient.user.last_name} {obj.patient.user.first_name}"

    @admin.display(description='Médecin', ordering='docteur__user__last_name')
    def get_docteur(self, obj):
        return f"Dr. {obj.docteur.user.last_name}"

    # BONUS : Afficher le statut avec des couleurs
    @admin.display(description='Statut', ordering='statut')
    def get_statut_colored(self, obj):
        colors = {
            'EN_ATTENTE': 'orange',
            'CONFIRME': 'green',
            'ANNULE': 'red',
            'TERMINE': 'blue',
        }
        color = colors.get(obj.statut, 'black')
        # On affiche le texte du statut en gras et en couleur
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            color, 
            obj.get_statut_display()
        )