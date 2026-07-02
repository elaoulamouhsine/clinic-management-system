from django.db import models
from django.db.models import Sum

class Facture(models.Model):
    """
    Table 'FACTURE' du diagramme.
    Liée 1..1 avec Consultation.
    """
    STATUT_CHOICES = [
        ('NON_PAYE', 'Non payée'),
        ('PAYE', 'Payée'),
        ('EN_ATTENTE', 'En attente'),
    ]

    consultation = models.OneToOneField(
        'consultations.Consultation',
        on_delete=models.CASCADE,
        related_name='facture',
        verbose_name="Consultation associée"
    )

    date_facture = models.DateField(auto_now_add=True, verbose_name="Date de facturation")

    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant Total (DH)",
        blank=True, null=True,
        help_text="Laisser vide pour calculer automatiquement selon les actes."
    )

    statut_paiement = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='NON_PAYE',
        verbose_name="Statut du paiement"
    )

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour calculer automatiquement le montant
        si l'utilisateur ne l'a pas saisi.
        """
        if not self.montant and self.consultation_id:
            total = self.consultation.actes.aggregate(total=Sum('tarif'))['total']
            self.montant = total if total else 0.00

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture #{self.id} - {self.get_statut_paiement_display()}"
