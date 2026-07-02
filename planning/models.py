from django.db import models
from django.core.exceptions import ValidationError

class RDV(models.Model):
    """
    Modèle représentant un Rendez-vous médical.
    Relation: Un Patient prend un RDV avec un Docteur.
    """

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRME', 'Confirmé'),
        ('ANNULE', 'Annulé'),
        ('TERMINE', 'Terminé'),
    ]

    docteur = models.ForeignKey(
        'accounts.Docteur',
        on_delete=models.CASCADE,
        related_name='rdvs_assures',
        verbose_name="Médecin"
    )

    patient = models.ForeignKey(
        'accounts.Patient',
        on_delete=models.CASCADE,
        related_name='rdvs_pris',
        verbose_name="Patient"
    )

    date = models.DateField(verbose_name="Date du RDV")
    heure = models.TimeField(verbose_name="Heure du RDV")

    motif = models.CharField(max_length=255, blank=True, verbose_name="Motif de consultation")
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.patient_id is None:
            return

        conflit = RDV.objects.filter(
            patient=self.patient,
            date=self.date,
            heure=self.heure
        ).exclude(pk=self.pk)

        if conflit.exists():
            raise ValidationError("Rendez-vous déjà existant.")

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-date', '-heure']

        constraints = [
            models.UniqueConstraint(
                fields=['docteur', 'date', 'heure'],
                name='unique_rdv_creneau_docteur'
            ),
            models.UniqueConstraint(
                fields=['patient', 'date', 'heure'],
                name='unique_rdv_creneau_patient'
            )
        ]

    def __str__(self):
        return f"RDV le {self.date} à {self.heure} - Dr. {self.docteur.user.last_name}"
