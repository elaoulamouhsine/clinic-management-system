from django.contrib import admin
from .models import Mutuelle, Vaccin, Allergie, Maladie


@admin.register(Mutuelle)
class MutuelleAdmin(admin.ModelAdmin):
    list_display = ('nom_orga', 'type_orga', 'taux_remise')
    search_fields = ('nom_orga',)

@admin.register(Vaccin)
class VaccinAdmin(admin.ModelAdmin):
    search_fields = ('nom_vac',)

@admin.register(Allergie)
class AllergieAdmin(admin.ModelAdmin):
    search_fields = ('nom_alrg',)

@admin.register(Maladie)
class MaladieAdmin(admin.ModelAdmin):
    search_fields = ('nom_mal',)
