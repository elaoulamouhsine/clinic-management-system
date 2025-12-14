from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modèle d'utilisateur unifié gérant l'authentification pour tous les acteurs.
    Remplace le modèle par défaut de Django.
    
    Les champs 'first_name' (Prénom) et 'last_name' (Nom) sont déjà inclus 
    dans AbstractUser et seront utilisés pour tous les acteurs (Patient, Médecin, etc.).
    """
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"         # Superuser / Admin technique
        SECRETAIRE = "SECRETAIRE", "Secrétaire"   # Gestion administrative 
        DOCTEUR = "DOCTEUR", "Docteur"            # Gestion médicale 
        PATIENT = "PATIENT", "Patient"            # Bénéficiaire des soins 

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.PATIENT,
        verbose_name="Rôle utilisateur"
    )


    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Docteur(models.Model):
    """
    Profil métier pour le Médecin.
    Source: Dictionnaire de données 
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile_docteur',
        limit_choices_to={'role': User.Role.DOCTEUR}
    )
    
    # Spécifique au médecin selon le MCD
    specialite = models.CharField(
        max_length=50, 
        verbose_name="Spécialité médicale",
        default="Généraliste" # Valeur par défaut utile
    )

    def __str__(self):
        return f"Dr. {self.user.last_name} {self.user.first_name} - {self.specialite}"


class Patient(models.Model):
    """
    Profil métier pour le Patient.
    Contient les données administratives requises par le RG1 et le dictionnaire[cite: 62].
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile_patient',
        limit_choices_to={'role': User.Role.PATIENT}
    )

    # [cite_start]RG1 : Le patient est identifié de manière unique (ici par CIN en plus de l'ID) [cite: 42]
    # [cite_start]Dictionnaire des données : CIN Pat (AN, 20, Unique) [cite: 62]
    cin = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Numéro CIN",
        help_text="Carte d'Identité Nationale"
    )

    # [cite_start]Dictionnaire des données : Adresse Pat (AN, 255) [cite: 67]
    adresse = models.TextField(
        verbose_name="Adresse complète",
        blank=True
    )

    # [cite_start]Dictionnaire des données : Date Naiss Pat (Date) [cite: 67]
    date_naissance = models.DateField(
        verbose_name="Date de naissance"
    )
    # TODO
    # [cite_start]RG2 : Un patient peut être affilié à une mutuelle [cite: 43]
    # Utilisation d'une "Lazy Reference" (chaîne de caractères) pour pointer vers l'app 'dossiers'
    # Cela évite l'erreur "ImportError: cannot import name..."
    #mutuelle = models.ForeignKey(
    #    'dossiers.Mutuelle', 
    #    on_delete=models.SET_NULL, 
    #    null=True, 
    #    blank=True,
    #    related_name='affilies',
    #    verbose_name="Organisme de Mutuelle" )

    #class Meta:
    #    verbose_name = "Dossier Administratif Patient"
    #    verbose_name_plural = "Dossiers Patients"
    #    ordering = ['user__last_name']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} (CIN: {self.cin})"