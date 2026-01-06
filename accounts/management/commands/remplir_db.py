import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.utils import IntegrityError

# Import des modèles
from accounts.models import User, Docteur, Patient
from planning.models import RDV

# Imports précis depuis votre dossiers/models.py
from dossiers.models import (
    Mutuelle, Vaccin, Allergie, Maladie, 
    Vaccination, AntecedentAllergie, AntecedentMaladie
)

fake = Faker('fr_FR')

class Command(BaseCommand):
    help = "Remplit la base de données avec des fausses données de test complètes"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔨 Début de la génération des données...")

        # ==========================================
        # 1. CATALOGUES (App DOSSIERS)
        # ==========================================
        self.stdout.write("- Création des catalogues médicaux...")
        
        # --- Mutuelles ---
        mutuelles_data = [
            ('CNOPS', 'Public', 80.00), ('CNSS', 'Public', 70.00),
            ('AXA Assurance', 'Privé', 90.00), ('Wafa Assurance', 'Privé', 85.00)
        ]
        list_mutuelles = []
        for nom, type_org, taux in mutuelles_data:
            m, _ = Mutuelle.objects.get_or_create(
                nom_orga=nom, 
                defaults={'type_orga': type_org, 'taux_remise': taux}
            )
            list_mutuelles.append(m)

        # --- Vaccins ---
        vaccins_noms = ['Pfizer', 'AstraZeneca', 'BCG', 'Tétanos', 'Rougeole', 'Hépatite B']
        for v in vaccins_noms:
            Vaccin.objects.get_or_create(nom_vac=v)

        # --- Allergies ---
        allergies_liste = [
            'Pollen', 'Acariens', 'Pénicilline', 'Arachides', 
            'Fruits de mer', 'Gluten', 'Latex', 'Piqûres d\'insectes'
        ]
        for a in allergies_liste:
            Allergie.objects.get_or_create(nom_alrg=a)

        # --- Maladies ---
        maladies_liste = [
            'Hypertension artérielle', 'Diabète de type 1', 'Diabète de type 2', 
            'Asthme', 'Migraine chronique', 'Arthrite', 'Cholestérol', 'Gastrite'
        ]
        for m in maladies_liste:
            Maladie.objects.get_or_create(nom_mal=m)


        # ==========================================
        # 2. UTILISATEURS (Médecins & Patients)
        # ==========================================
        self.stdout.write("- Création des comptes utilisateurs...")
        
        # --- Médecins ---
        specialites = ['Généraliste', 'Cardiologue', 'Dermatologue', 'Pédiatre', 'Dentiste']
        list_docteurs = []

        for i in range(5): 
            username = f"doc_{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, password='123', email=fake.email(),
                    first_name=fake.first_name(), last_name=fake.last_name(),
                    role=User.Role.DOCTEUR
                )
                doc = Docteur.objects.create(user=user, specialite=random.choice(specialites))
                list_docteurs.append(doc)
            else:
                list_docteurs.append(Docteur.objects.get(user__username=username))

        # --- Patients ---
        list_patients = []
        for i in range(20):
            username = f"patient_{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, password='123', email=fake.email(),
                    first_name=fake.first_name(), last_name=fake.last_name(),
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
        # 3. DOSSIER MÉDICAL (Liaisons)
        # ==========================================
        self.stdout.write("- Remplissage des dossiers médicaux...")

        # Récupération des catalogues
        all_vaccins = list(Vaccin.objects.all())
        all_allergies = list(Allergie.objects.all())
        all_maladies = list(Maladie.objects.all())
        
        # Choix exacts de votre modèle AntecedentAllergie
        intensite_choices = ['Faible', 'Moyenne', 'Grave']

        for patient in list_patients:
            
            # --- A. Vaccinations ---
            nb_vac = random.randint(0, 3)
            mes_vaccins = random.sample(all_vaccins, nb_vac) if len(all_vaccins) >= nb_vac else all_vaccins
            
            for v in mes_vaccins:
                date_inj = fake.date_between(start_date='-10y', end_date='today')
                Vaccination.objects.get_or_create(
                    patient=patient,
                    vaccin=v,
                    defaults={
                        'date_injection': date_inj,
                        'observation': fake.sentence(nb_words=5) # Champ observation rempli
                    }
                )

            # --- B. Allergies (Antécédents) ---
            nb_alg = random.randint(0, 2)
            mes_allergies = random.sample(all_allergies, nb_alg) if len(all_allergies) >= nb_alg else all_allergies

            for a in mes_allergies:
                AntecedentAllergie.objects.get_or_create(
                    patient=patient,
                    allergie=a,
                    defaults={
                        'intensite': random.choice(intensite_choices), # Champ intensité correct
                        'commentaire': fake.text(max_nb_chars=50)      # Champ commentaire rempli
                    }
                )

            # --- C. Maladies (Antécédents) ---
            nb_mal = random.randint(0, 2)
            mes_maladies = random.sample(all_maladies, nb_mal) if len(all_maladies) >= nb_mal else all_maladies

            for m in mes_maladies:
                date_diag = fake.date_between(start_date='-5y', end_date='-1y')
                is_chronic = random.choice([True, False])
                
                AntecedentMaladie.objects.get_or_create(
                    patient=patient,
                    maladie=m,
                    defaults={
                        'date_diagnostic': date_diag,
                        'est_chronique': is_chronic # Champ est_chronique rempli
                    }
                )

        # ==========================================
        # 4. PLANNING (RDV)
        # ==========================================
        self.stdout.write("- Génération des Rendez-vous...")
        
        # On vide les RDV pour éviter les conflits et repartir sur un planning propre
        RDV.objects.all().delete() 

        compteur_rdv = 0
        for _ in range(60): # Tentative de créer 60 RDV
            patient = random.choice(list_patients)
            docteur = random.choice(list_docteurs)
            
            # Génération d'un créneau
            jours_delta = random.randint(-10, 10)
            date_rdv = timezone.now().date() + timedelta(days=jours_delta)
            heure_rdv = f"{random.randint(9, 17)}:00"

            status = 'EN_ATTENTE'
            if jours_delta < 0: status = 'TERMINE'
            elif jours_delta == 0: status = 'CONFIRME'

            try:
                # On tente de créer le RDV
                # Le système de contrainte unique de la BDD peut lever une erreur
                # si le créneau est déjà pris, donc on utilise un try/except
                RDV.objects.create(
                    docteur=docteur,
                    patient=patient,
                    date=date_rdv,
                    heure=heure_rdv,
                    motif=fake.sentence(nb_words=6),
                    statut=status
                )
                compteur_rdv += 1
            except IntegrityError:
                # Si conflit (Docteur ou Patient déjà occupé), on ignore simplement ce RDV
                continue

        self.stdout.write(self.style.SUCCESS(f"✅ Base de données remplie avec succès ! ({compteur_rdv} RDV créés)"))