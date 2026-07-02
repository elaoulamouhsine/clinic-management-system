from django.db import models


class Mutuelle(models.Model):
    """
    Entité MUTUELLE du MCD.
    Gère les organismes d'assurance.
    """
    nom_orga = models.CharField(max_length=100, verbose_name="Nom de l'organisme")

    type_orga = models.CharField(max_length=50, verbose_name="Type d'organisme")

    taux_remise = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux de remise (%)",
        help_text="Pourcentage de couverture (ex: 80.00)"
    )

    def __str__(self):
        return f"{self.nom_orga} ({self.taux_remise}%)"


class Vaccin(models.Model):
    """
    Entité VACCIN du MCD.
    """
    nom_vac = models.CharField(max_length=50, verbose_name="Nom du vaccin")

    def __str__(self):
        return self.nom_vac


class Allergie(models.Model):
    """
    Entité ALLERGIE du MCD.
    """
    nom_alrg = models.CharField(max_length=50, verbose_name="Nom de l'allergie")

    def __str__(self):
        return self.nom_alrg


class Maladie(models.Model):
    """
    Entité MALADIE du MCD.
    """
    nom_mal = models.CharField(max_length=50, verbose_name="Nom de la maladie")

    def __str__(self):
        return self.nom_mal


class Vaccination(models.Model):
    """
    Implémente la relation 'Se_Vacciner'.
    """
    patient = models.ForeignKey(
        'accounts.Patient',
        on_delete=models.CASCADE,
        related_name='vaccinations'
    )
    vaccin = models.ForeignKey(Vaccin, on_delete=models.CASCADE)

    date_injection = models.DateField(verbose_name="Date de l'injection")
    observation = models.TextField(blank=True, verbose_name="Observations")

    class Meta:
        verbose_name = "Vaccination"
        verbose_name_plural = "Vaccinations"

    def __str__(self):
        return f"{self.patient} - {self.vaccin}"


class AntecedentAllergie(models.Model):
    """
    [cite_start]Implémente la relation 'Avoir'[cite: 104].
    """
    patient = models.ForeignKey(
        'accounts.Patient',
        on_delete=models.CASCADE,
        related_name='antecedents_allergies'
    )
    allergie = models.ForeignKey(Allergie, on_delete=models.CASCADE)

    intensite = models.CharField(
        max_length=20,
        choices=[('Faible', 'Faible'), ('Moyenne', 'Moyenne'), ('Grave', 'Grave')],
        default='Faible',
        verbose_name="Intensité"
    )
    commentaire = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Antécédent Allergie"

    def __str__(self):
        return f"{self.patient} - {self.allergie} ({self.intensite})"


class AntecedentMaladie(models.Model):
    """
    [cite_start]Implémente la relation 'Souffrir'[cite: 107].
    """
    patient = models.ForeignKey(
        'accounts.Patient',
        on_delete=models.CASCADE,
        related_name='antecedents_maladies'
    )
    maladie = models.ForeignKey(Maladie, on_delete=models.CASCADE)

    date_diagnostic = models.DateField(null=True, blank=True, verbose_name="Date du diagnostic")
    est_chronique = models.BooleanField(default=False, verbose_name="Maladie Chronique")

    class Meta:
        verbose_name = "Antécédent Maladie"

    def __str__(self):
        etat = "Chronique" if self.est_chronique else "Ponctuelle"
        return f"{self.patient} - {self.maladie} ({etat})"
