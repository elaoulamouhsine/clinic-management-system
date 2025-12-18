from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Docteur, Patient

# --- IMPORTATION DES MODÈLES DE L'AUTRE APP ---
from dossiers.models import Vaccination, AntecedentAllergie, AntecedentMaladie

# 1. Définition des "Inlines" (Tableaux imbriqués)

class VaccinationInline(admin.TabularInline):
    model = Vaccination
    extra = 1  # Affiche une ligne vide prête à remplir
    autocomplete_fields = ['vaccin'] # Barre de recherche pour le vaccin (optionnel mais pratique)

class AllergieInline(admin.TabularInline):
    model = AntecedentAllergie
    extra = 1
    autocomplete_fields = ['allergie']

class MaladieInline(admin.TabularInline):
    model = AntecedentMaladie
    extra = 1
    autocomplete_fields = ['maladie']

# 2. Configuration Admin existante (Mise à jour)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Métier', {'fields': ('role',)}),
    )

class DocteurAdmin(admin.ModelAdmin):
    list_display = ('get_nom', 'get_prenom', 'specialite')
    
    @admin.display(description='Nom')
    def get_nom(self, obj):
        return obj.user.last_name

    @admin.display(description='Prénom')
    def get_prenom(self, obj):
        return obj.user.first_name

class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_nom', 'get_prenom', 'cin', 'mutuelle')
    search_fields = ('user__last_name', 'cin')
    
    # C'EST ICI QU'ON LIE LES DEUX APPS :
    inlines = [VaccinationInline, AllergieInline, MaladieInline]

    @admin.display(description='Utilisateur', ordering='user__username')
    def get_username(self, obj):
        return obj.user.username  # On récupère le champ username du User lié

    @admin.display(description='Nom')
    def get_nom(self, obj):
        return obj.user.last_name

    @admin.display(description='Prénom')
    def get_prenom(self, obj):
        return obj.user.first_name

# Enregistrement final
admin.site.register(User, CustomUserAdmin)
admin.site.register(Docteur, DocteurAdmin)
admin.site.register(Patient, PatientAdmin)