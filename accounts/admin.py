from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Docteur, Patient

# 1. CustomUserAdmin (Rien ne change ici)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Métier', {'fields': ('role',)}),
    )

# 2. Configuration pour DOCTEUR
class DocteurAdmin(admin.ModelAdmin):
    # On appelle nos fonctions personnalisées ici
    list_display = ('get_nom', 'get_prenom', 'specialite')
    
    # Barre de recherche (On cherche via le User lié)
    search_fields = ('user__last_name', 'user__first_name', 'specialite')

    # --- Fonctions pour récupérer les infos du User ---
    
    @admin.display(description='Nom', ordering='user__last_name')
    def get_nom(self, obj):
        return obj.user.last_name

    @admin.display(description='Prénom', ordering='user__first_name')
    def get_prenom(self, obj):
        return obj.user.first_name

# 3. Configuration pour PATIENT
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_nom', 'get_prenom', 'cin','adresse', 'date_naissance')
    search_fields = ('user__last_name', 'user__first_name', 'cin')
    list_filter = ('user__is_active',) # Filtre utile sur le côté

    @admin.display(description='Nom', ordering='user__last_name')
    def get_nom(self, obj):
        return obj.user.last_name

    @admin.display(description='Prénom', ordering='user__first_name')
    def get_prenom(self, obj):
        return obj.user.first_name

# Enregistrement
admin.site.register(User, CustomUserAdmin)
admin.site.register(Docteur, DocteurAdmin)
admin.site.register(Patient, PatientAdmin)

# for users passwords pathern is testuser pass is user1111 or user2222 .....