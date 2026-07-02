from django.contrib import admin
from .models import Acte, Consultation, Ordonnance

@admin.register(Acte)
class ActeAdmin(admin.ModelAdmin):
    """
    Gestion du catalogue des actes médicaux.
    """
    list_display = ('nom', 'tarif')
    search_fields = ('nom',)
    ordering = ('nom',)

class OrdonnanceInline(admin.StackedInline):
    """
    Permet de voir/modifier l'ordonnance directement dans la page de la consultation.
    """
    model = Ordonnance
    extra = 0
    can_delete = True

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('date_consultation', 'get_patient', 'get_medecin', 'est_revision', 'tarif_total')
    list_filter = ('date_consultation', 'est_revision')
    search_fields = ('rdv__patient__user__last_name', 'rdv__patient__user__first_name', 'diagnostic')
    autocomplete_fields = ['rdv']

    inlines = [OrdonnanceInline]

    filter_horizontal = ('actes',)

    def get_patient(self, obj):
        return f"{obj.rdv.patient.user.last_name} {obj.rdv.patient.user.first_name}"
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'rdv__patient__user__last_name'

    def get_medecin(self, obj):
        return f"Dr. {obj.rdv.docteur.user.last_name}"
    get_medecin.short_description = 'Médecin'

    def tarif_total(self, obj):
        """Calcule la somme des actes réalisés pour cette consultation"""
        total = sum(acte.tarif for acte in obj.actes.all())
        return f"{total} DH"
    tarif_total.short_description = 'Total Actes'

@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_consultation_str', 'date_ordonnance')
    search_fields = ('traitement',)

    def get_consultation_str(self, obj):
        return str(obj.consultation)
    get_consultation_str.short_description = 'Consultation Associée'
