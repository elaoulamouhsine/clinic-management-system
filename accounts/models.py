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
        ADMIN = "ADMIN", "Administrateur"
        SECRETAIRE = "SECRETAIRE", "Secrétaire"
        DOCTEUR = "DOCTEUR", "Docteur"
        PATIENT = "PATIENT", "Patient"

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
    [cite_start]Source: Dictionnaire de données [cite: 67]
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile_docteur',
        limit_choices_to={'role': User.Role.DOCTEUR}
    )

    specialite = models.CharField(
        max_length=50,
        verbose_name="Spécialité médicale",
        default="Généraliste"
    )

    class Meta:
        verbose_name = "Médecin"
        verbose_name_plural = "Médecins"

    def __str__(self):
        return f"Dr. {self.user.last_name} {self.user.first_name} - {self.specialite}"


class Patient(models.Model):
    """
    Profil métier pour le Patient.
    [cite_start]Contient les données administratives requises par le RG1 [cite: 42] [cite_start]et le dictionnaire[cite: 62].
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile_patient',
        limit_choices_to={'role': User.Role.PATIENT}
    )

    cin = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro CIN",
        help_text="Carte d'Identité Nationale"
    )

    adresse = models.TextField(
        verbose_name="Adresse complète",
        blank=True
    )

    date_naissance = models.DateField(
        verbose_name="Date de naissance"
    )

    mutuelle = models.ForeignKey(
        'dossiers.Mutuelle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affilies',
        verbose_name="Organisme de Mutuelle"
    )

    class Meta:
        verbose_name = "Dossier Administratif Patient"
        verbose_name_plural = "Dossiers Patients"
        ordering = ['user__last_name']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} (CIN: {self.cin})"
