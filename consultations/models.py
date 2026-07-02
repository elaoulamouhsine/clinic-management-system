from django.db import models

class Acte(models.Model):
    """
    Catalogue des actes médicaux (ex: Consultation généraliste, ECG, Echographie...)
    Table 'ACTE' du diagramme.
    """
    nom = models.CharField(max_length=150, verbose_name="Nom de l'acte")
    tarif = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tarif")

    def __str__(self):
        return f"{self.nom} ({self.tarif} DH)"


class Consultation(models.Model):
    """
    Table 'CONSULTATION' du diagramme.
    Reliée au RDV (planning) et peut contenir plusieurs Actes.
    """
    rdv = models.OneToOneField(
        'planning.RDV',
        on_delete=models.CASCADE,
        related_name='consultation',
        verbose_name="Rendez-vous associé"
    )

    actes = models.ManyToManyField(
        Acte,
        related_name='consultations',
        verbose_name="Actes réalisés"
    )

    consultation_origine = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        verbose_name="Consultation d'origine (si révision)"
    )

    date_consultation = models.DateField(auto_now_add=True, verbose_name="Date de consultation")
    diagnostic = models.TextField(verbose_name="Diagnostic")
    commentaires = models.TextField(blank=True, null=True, verbose_name="Commentaires")

    est_revision = models.BooleanField(default=False, verbose_name="Est une révision")

    def save(self, *args, **kwargs):
        if self.consultation_origine:
            self.est_revision = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consultation du {self.date_consultation} - {self.rdv.patient}"


class Ordonnance(models.Model):
    """
    Table 'ORDONNANCE' du diagramme.
    Relation "Délivrer" 1..1 avec Consultation.
    """
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name='ordonnance'
    )

    date_ordonnance = models.DateField(auto_now_add=True, verbose_name="Date de l'ordonnance")
    traitement = models.TextField(
        verbose_name="Traitement (Médicaments et posologie)",
        help_text="Détaillez les médicaments prescrits ici."
    )

    def __str__(self):
        return f"Ordonnance pour {self.consultation.rdv.patient}"
