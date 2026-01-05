from django.db import models

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

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-date', '-heure'] # Trie par défaut du plus récent au plus ancien
        
        # CONTRAINTE D'UNICITÉ (Bonus Pro)
        # Empêche de créer deux RDV pour le même docteur à la même heure
        constraints = [
            models.UniqueConstraint(
                fields=['docteur', 'date', 'heure'], 
                name='unique_rdv_creneau_docteur'
            )
        ]

    def __str__(self):
        return f"RDV le {self.date} à {self.heure} - Dr. {self.docteur.user.last_name}"