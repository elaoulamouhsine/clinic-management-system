from django.contrib import admin
from django.utils.html import format_html
from .models import RDV

@admin.register(RDV)
class RDVAdmin(admin.ModelAdmin):
    list_display = ('date', 'heure', 'get_patient', 'get_docteur', 'get_statut_colored')

    list_filter = ('statut', 'date', 'docteur')

    search_fields = (
        'patient__user__last_name',
        'patient__user__first_name',
        'patient__cin',
        'docteur__user__last_name'
    )

    date_hierarchy = 'date'

    ordering = ['-date', '-heure']

    @admin.display(description='Patient', ordering='patient__user__last_name')
    def get_patient(self, obj):
        return f"{obj.patient.user.last_name} {obj.patient.user.first_name}"

    @admin.display(description='Médecin', ordering='docteur__user__last_name')
    def get_docteur(self, obj):
        return f"Dr. {obj.docteur.user.last_name}"

    @admin.display(description='Statut', ordering='statut')
    def get_statut_colored(self, obj):
        colors = {
            'EN_ATTENTE': 'orange',
            'CONFIRME': 'green',
            'ANNULE': 'red',
            'TERMINE': 'blue',
        }
        color = colors.get(obj.statut, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_statut_display()
        )
