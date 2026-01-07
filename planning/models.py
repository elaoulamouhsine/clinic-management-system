from django.db import models
from django.core.exceptions import ValidationError # <--- 1. Import nécessaire
class RDV(models.Model):
    """
    Modèle représentant un Rendez-vous médical.
    Relation: Un Patient prend un RDV avec un Docteur.
    """

    # --- 1. STATUS DU RDV ---
    # Indispensable pour la gestion du workflow (Attente -> Confirmé -> Terminé)
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRME', 'Confirmé'),
        ('ANNULE', 'Annulé'),
        ('TERMINE', 'Terminé'),
    ]

    # --- 2. RELATIONS (Clés Étrangères) ---
    
    # Relation "Assurer" (Visible sur votre diagramme)
    # On utilise 'accounts.Docteur' pour éviter les imports circulaires
    docteur = models.ForeignKey(
        'accounts.Docteur',
        on_delete=models.CASCADE, 
        related_name='rdvs_assures', # Permet: docteur.rdvs_assures.all()
        verbose_name="Médecin"
    )

    patient = models.ForeignKey(
        'accounts.Patient',
        on_delete=models.CASCADE,
        related_name='rdvs_pris',    # Permet: patient.rdvs_pris.all()
        verbose_name="Patient"
    )

    # --- 3. INFORMATIONS TEMPORELLES ---
    
    date = models.DateField(verbose_name="Date du RDV")
    heure = models.TimeField(verbose_name="Heure du RDV")
    
    # --- 4. AUTRES CHAMPS ---
    motif = models.CharField(max_length=255, blank=True, verbose_name="Motif de consultation")
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='EN_ATTENTE',
        verbose_name="Statut"
    )
    
    # Horodatage technique (utile pour le tri)
    date_creation = models.DateTimeField(auto_now_add=True)

    # --- VALIDATION LOGIQUE (Pour afficher un beau message d'erreur) ---
def clean(self):
        super().clean()
        
        # --- LIGNE CRUCIALE A AJOUTER ---
        # Si le patient n'est pas encore assigné (cas du formulaire), on saute la vérif
        if self.patient_id is None:
            return 
        # --------------------------------

        # Votre logique de conflit existante
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
        
        # CONTRAINTES DE BASE DE DONNÉES (Le blindage ultime)
        constraints = [
            # 1. Contrainte Docteur (Déjà existante) : Un docteur ne peut pas avoir 2 RDV en même temps
            models.UniqueConstraint(
                fields=['docteur', 'date', 'heure'], 
                name='unique_rdv_creneau_docteur'
            ),
            # 2. Contrainte Patient (NOUVELLE) : Un patient ne peut pas avoir 2 RDV en même temps
            models.UniqueConstraint(
                fields=['patient', 'date', 'heure'], 
                name='unique_rdv_creneau_patient'
            )
        ]

def __str__(self):
        return f"RDV le {self.date} à {self.heure} - Dr. {self.docteur.user.last_name}"