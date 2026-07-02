from django.contrib import admin
from .models import Facture

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_facture', 'get_patient', 'montant', 'statut_paiement')
    list_filter = ('statut_paiement', 'date_facture')
    search_fields = ('consultation__rdv__patient__user__last_name',)

    list_editable = ('statut_paiement',)

    def get_patient(self, obj):
        return obj.consultation.rdv.patient
    get_patient.short_description = 'Patient'
