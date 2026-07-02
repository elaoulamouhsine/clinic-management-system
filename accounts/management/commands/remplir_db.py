import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.utils import IntegrityError

from accounts.models import User, Docteur, Patient
from planning.models import RDV
from dossiers.models import (
    Mutuelle, Vaccin, Allergie, Maladie,
    Vaccination, AntecedentAllergie, AntecedentMaladie
)

from consultations.models import Acte, Consultation, Ordonnance
from facturation.models import Facture

fake = Faker('fr_FR')

class Command(BaseCommand):
    help = "Remplit la base de données avec des fausses données de test complètes (y compris Consultations et Factures)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Début de la génération des données")

        self.stdout.write("- Création des catalogues (Médicaux & Actes)")

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

        vaccins_noms = ['Pfizer', 'AstraZeneca', 'BCG', 'Tétanos', 'Rougeole', 'Hépatite B']
        for v in vaccins_noms:
            Vaccin.objects.get_or_create(nom_vac=v)

        allergies_liste = [
            'Pollen', 'Acariens', 'Pénicilline', 'Arachides',
            'Fruits de mer', 'Gluten', 'Latex', 'Piqûres d\'insectes'
        ]
        for a in allergies_liste:
            Allergie.objects.get_or_create(nom_alrg=a)

        maladies_liste = [
            'Hypertension artérielle', 'Diabète de type 1', 'Diabète de type 2',
            'Asthme', 'Migraine chronique', 'Arthrite', 'Cholestérol', 'Gastrite'
        ]
        for m in maladies_liste:
            Maladie.objects.get_or_create(nom_mal=m)

        actes_data = [
            ('Consultation Généraliste', 200.00),
            ('Consultation Spécialiste', 300.00),
            ('Échographie', 400.00),
            ('Electrocardiogramme (ECG)', 250.00),
            ('Certificat médical', 100.00),
            ('Petite chirurgie', 600.00),
            ('Vaccination (Acte)', 150.00)
        ]
        list_actes = []
        for nom, tarif in actes_data:
            act, _ = Acte.objects.get_or_create(nom=nom, defaults={'tarif': tarif})
            list_actes.append(act)


        self.stdout.write("Création des comptes utilisateurs")

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

        self.stdout.write("- Remplissage des dossiers médicaux...")

        all_vaccins = list(Vaccin.objects.all())
        all_allergies = list(Allergie.objects.all())
        all_maladies = list(Maladie.objects.all())
        intensite_choices = ['Faible', 'Moyenne', 'Grave']

        for patient in list_patients:
            nb_vac = random.randint(0, 3)
            mes_vaccins = random.sample(all_vaccins, nb_vac) if len(all_vaccins) >= nb_vac else all_vaccins
            for v in mes_vaccins:
                Vaccination.objects.get_or_create(
                    patient=patient, vaccin=v,
                    defaults={
                        'date_injection': fake.date_between(start_date='-10y', end_date='today'),
                        'observation': fake.sentence(nb_words=5)
                    }
                )

            nb_alg = random.randint(0, 2)
            mes_allergies = random.sample(all_allergies, nb_alg) if len(all_allergies) >= nb_alg else all_allergies
            for a in mes_allergies:
                AntecedentAllergie.objects.get_or_create(
                    patient=patient, allergie=a,
                    defaults={
                        'intensite': random.choice(intensite_choices),
                        'commentaire': fake.text(max_nb_chars=50)
                    }
                )

            nb_mal = random.randint(0, 2)
            mes_maladies = random.sample(all_maladies, nb_mal) if len(all_maladies) >= nb_mal else all_maladies
            for m in mes_maladies:
                AntecedentMaladie.objects.get_or_create(
                    patient=patient, maladie=m,
                    defaults={
                        'date_diagnostic': fake.date_between(start_date='-5y', end_date='-1y'),
                        'est_chronique': random.choice([True, False])
                    }
                )

        self.stdout.write("Génération des Rendez-vous")

        RDV.objects.all().delete()

        compteur_rdv = 0
        list_rdv_created = []

        for _ in range(60):
            patient = random.choice(list_patients)
            docteur = random.choice(list_docteurs)

            jours_delta = random.randint(-5, 7)
            date_rdv = timezone.now().date() + timedelta(days=jours_delta)
            heure_rdv = f"{random.randint(9, 17)}:00"

            status = 'EN_ATTENTE'
            if jours_delta < 0: status = 'TERMINE'
            elif jours_delta == 0: status = 'CONFIRME'

            try:
                rdv = RDV.objects.create(
                    docteur=docteur,
                    patient=patient,
                    date=date_rdv,
                    heure=heure_rdv,
                    motif=fake.sentence(nb_words=6),
                    statut=status
                )
                compteur_rdv += 1
                list_rdv_created.append(rdv)
            except IntegrityError:
                continue

        self.stdout.write("Génération des Consultations, Ordonnances et Factures")

        compteur_cons = 0
        compteur_fact = 0

        rdvs_termines = [r for r in list_rdv_created if r.statut == 'TERMINE']

        for rdv in rdvs_termines:
            consultation = Consultation.objects.create(
                rdv=rdv,
                diagnostic=f"Patient se plaint de : {fake.sentence()}\nObservation : {fake.text(max_nb_chars=100)}",
                commentaires=fake.text(max_nb_chars=50),
                est_revision=random.choice([True, False]) if random.random() > 0.8 else False
            )

            nb_actes = random.randint(1, 2)
            actes_choisis = random.sample(list_actes, nb_actes)
            consultation.actes.set(actes_choisis)

            if random.random() < 0.8:
                Ordonnance.objects.create(
                    consultation=consultation,
                    traitement=f"- Doliprane 1000mg (3x/jour)\n- {fake.word().capitalize()} 500mg (1x/jour le soir)\n- Repos pendant 3 jours."
                )

            statut_pay = random.choice(['PAYE', 'NON_PAYE', 'EN_ATTENTE'])

            Facture.objects.create(
                consultation=consultation,
                statut_paiement=statut_pay
            )

            compteur_cons += 1
            compteur_fact += 1

        self.stdout.write(self.style.SUCCESS(f"Terminé !"))
        self.stdout.write(f"   - {compteur_rdv} RDV créés")
        self.stdout.write(f"   - {compteur_cons} Consultations générées (pour les RDV terminés)")
        self.stdout.write(f"   - {compteur_fact} Factures générées")
