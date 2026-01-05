import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

# Import des modèles
from accounts.models import User, Docteur, Patient
# On ajoute Allergie et Maladie aux imports
from dossiers.models import Mutuelle, Vaccin, Allergie, Maladie
from planning.models import RDV

fake = Faker('fr_FR')

class Command(BaseCommand):
    help = "Remplit la base de données avec des fausses données de test"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔨 Début de la génération des données...")

        # ==========================================
        # 1. CATALOGUES (App DOSSIERS)
        # ==========================================
        self.stdout.write("- Création des catalogues médicaux (Mutuelles, Vaccins)...")
        
        # --- Mutuelles ---
        mutuelles_data = [
            ('CNOPS', 'Public', 80.00), ('CNSS', 'Public', 70.00),
            ('AXA Assurance', 'Privé', 90.00), ('Wafa Assurance', 'Privé', 85.00)
        ]
        list_mutuelles = []
        for nom, type_org, taux in mutuelles_data:
            m, _ = Mutuelle.objects.get_or_create(nom_orga=nom, defaults={'type_orga': type_org, 'taux_remise': taux})
            list_mutuelles.append(m)

        # --- Vaccins ---
        vaccins_noms = ['Pfizer', 'AstraZeneca', 'BCG', 'Tétanos', 'Rougeole', 'Hépatite B']
        for v in vaccins_noms:
            Vaccin.objects.get_or_create(nom_vac=v)

        # ==========================================
        # 1.b NOUVEAU : ALLERGIES ET MALADIES
        # ==========================================
        self.stdout.write("- Création des catalogues Allergies et Maladies...")

        # --- Allergies ---
        allergies_liste = [
            'Pollen', 'Acariens', 'Pénicilline', 'Arachides', 
            'Fruits de mer', 'Gluten', 'Latex', 'Piqûres d\'insectes'
        ]
        for a in allergies_liste:
            # Attention : Assurez-vous que le champ est bien 'nom_alrg' dans votre modèle
            Allergie.objects.get_or_create(nom_alrg=a)

        # --- Maladies ---
        maladies_liste = [
            'Hypertension artérielle', 'Diabète de type 1', 'Diabète de type 2', 
            'Asthme', 'Migraine chronique', 'Arthrite', 'Cholestérol', 'Gastrite'
        ]
        for m in maladies_liste:
            # Attention : Assurez-vous que le champ est bien 'nom_mal' dans votre modèle
            Maladie.objects.get_or_create(nom_mal=m)


        # ==========================================
        # 2. MÉDECINS (App ACCOUNTS)
        # ==========================================
        self.stdout.write("- Création des médecins...")
        
        specialites = ['Généraliste', 'Cardiologue', 'Dermatologue', 'Pédiatre', 'Dentiste']
        list_docteurs = []

        for i in range(5): 
            username = f"doc_{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password='123',
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=User.Role.DOCTEUR
                )
                doc = Docteur.objects.create(
                    user=user,
                    specialite=random.choice(specialites)
                )
                list_docteurs.append(doc)
            else:
                list_docteurs.append(Docteur.objects.get(user__username=username))

        # ==========================================
        # 3. PATIENTS (App ACCOUNTS)
        # ==========================================
        self.stdout.write("- Création des patients...")
        
        list_patients = []
        for i in range(20):
            username = f"patient_{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password='123',
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=User.Role.PATIENT
                )
                pat = Patient.objects.create(
                    user=user,
                    cin=f"A{fake.random_number(digits=6)}",
                    date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    mutuelle=random.choice(list_mutuelles) if random.random() > 0.2 else None
                )
                list_patients.append(pat)
            else:
                list_patients.append(Patient.objects.get(user__username=username))

        # ==========================================
        # 4. PLANNING / RDV (App PLANNING)
        # ==========================================
        self.stdout.write("- Création des Rendez-vous...")
        
        RDV.objects.all().delete() 

        for _ in range(50):
            patient = random.choice(list_patients)
            docteur = random.choice(list_docteurs)
            jours_delta = random.randint(-10, 10)
            date_rdv = timezone.now().date() + timedelta(days=jours_delta)
            heure_rdv = f"{random.randint(9, 17)}:00"

            status = 'EN_ATTENTE'
            if jours_delta < 0: status = 'TERMINE'
            elif jours_delta == 0: status = 'CONFIRME'

            RDV.objects.get_or_create(
                docteur=docteur,
                date=date_rdv,
                heure=heure_rdv,
                defaults={
                    'patient': patient,
                    'motif': fake.sentence(nb_words=6),
                    'statut': status
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Base de données mise à jour avec Allergies et Maladies !"))