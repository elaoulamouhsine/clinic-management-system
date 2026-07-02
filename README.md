# Projet Systèmes d’Information & Bases de données

Application web de gestion d'un cabinet médical, développée avec **Django 5** et **PostgreSQL**.
Elle gère les patients, les rendez-vous, les consultations, les ordonnances, les dossiers
médicaux et la facturation, avec des espaces distincts selon le rôle de l'utilisateur.

---

## Fonctionnalités

- **Authentification par rôle** : Administrateur, Secrétaire, Docteur, Patient. Après connexion,
  chaque utilisateur est automatiquement redirigé vers son propre tableau de bord.
- **Secrétaire** : création des dossiers patients, vue d'ensemble des rendez-vous du jour.
- **Docteur** : salle d'attente du jour, création de consultations et d'ordonnances,
  suivi des revenus du jour.
- **Patient** : prise de rendez-vous, historique des consultations, ordonnances et factures.
- **Dossier médical** : mutuelles, vaccinations, antécédents (allergies, maladies).
- **Facturation** : génération de factures à partir des actes médicaux, avec calcul
  automatique du montant et suivi du statut de paiement.

---

## Architecture technique

- **Backend** : Django 5.0 (vues basées sur des classes, templates Django côté serveur).
- **Base de données** : PostgreSQL 16.
- **Frontend** : templates Django + Bootstrap 5 (pas de framework JavaScript).
- **Conteneurisation** : Docker + Docker Compose.

### Applications Django

| Application     | Rôle                                                                    |
|-----------------|-------------------------------------------------------------------------|
| `accounts`      | Utilisateur personnalisé, rôles, profils Docteur/Patient, tableaux de bord |
| `planning`      | Rendez-vous (RDV)                                                        |
| `consultations` | Consultations, actes médicaux, ordonnances                              |
| `facturation`   | Factures                                                                |
| `dossiers`      | Dossier médical : mutuelles, vaccins, allergies, maladies, antécédents  |

### Modèle conceptuel de données (MCD)

Modèle de données reconstitué à partir des modèles Django des cinq applications.

```mermaid
erDiagram
    USER ||--o| DOCTEUR : est
    USER ||--o| PATIENT : est

    MUTUELLE ||--o{ PATIENT : couvre

    DOCTEUR ||--o{ RDV : assure
    PATIENT ||--o{ RDV : prend

    RDV ||--o| CONSULTATION : genere
    CONSULTATION ||--o| ORDONNANCE : delivre
    CONSULTATION ||--o| FACTURE : facture
    CONSULTATION }o--o{ ACTE : comporte
    CONSULTATION ||--o{ CONSULTATION : revise

    PATIENT ||--o{ VACCINATION : recoit
    VACCIN ||--o{ VACCINATION : concerne

    PATIENT ||--o{ ANTECEDENT_ALLERGIE : presente
    ALLERGIE ||--o{ ANTECEDENT_ALLERGIE : concerne

    PATIENT ||--o{ ANTECEDENT_MALADIE : souffre
    MALADIE ||--o{ ANTECEDENT_MALADIE : concerne

    USER {
        int    id PK
        string username
        string first_name
        string last_name
        string email
        string role
        string password
    }

    DOCTEUR {
        int    id PK
        int    user_id FK
        string specialite
    }

    PATIENT {
        int    id PK
        int    user_id FK
        int    mutuelle_id FK
        string cin
        string adresse
        date   date_naissance
    }

    MUTUELLE {
        int     id PK
        string  nom_orga
        string  type_orga
        decimal taux_remise
    }

    RDV {
        int      id PK
        int      docteur_id FK
        int      patient_id FK
        date     date
        time     heure
        string   motif
        string   statut
        datetime date_creation
    }

    CONSULTATION {
        int    id PK
        int    rdv_id FK
        int    consultation_origine_id FK
        date   date_consultation
        string diagnostic
        string commentaires
        bool   est_revision
    }

    ACTE {
        int     id PK
        string  nom
        decimal tarif
    }

    ORDONNANCE {
        int    id PK
        int    consultation_id FK
        date   date_ordonnance
        string traitement
    }

    FACTURE {
        int     id PK
        int     consultation_id FK
        date    date_facture
        decimal montant
        string  statut_paiement
    }

    VACCIN {
        int    id PK
        string nom_vac
    }

    VACCINATION {
        int    id PK
        int    patient_id FK
        int    vaccin_id FK
        date   date_injection
        string observation
    }

    ALLERGIE {
        int    id PK
        string nom_alrg
    }

    ANTECEDENT_ALLERGIE {
        int    id PK
        int    patient_id FK
        int    allergie_id FK
        string intensite
        string commentaire
    }

    MALADIE {
        int    id PK
        string nom_mal
    }

    ANTECEDENT_MALADIE {
        int  id PK
        int  patient_id FK
        int  maladie_id FK
        date date_diagnostic
        bool est_chronique
    }
```

**Notes de lecture**

- **`USER` et les rôles** : l'authentification est unifiée dans une seule entité `USER`
  (champ `role`). Les rôles **Administrateur** et **Secrétaire** n'ont pas d'entité métier
  dédiée ; **Docteur** et **Patient** sont spécialisés par les entités `DOCTEUR` et
  `PATIENT`, reliées à `USER` par une relation **1‑à‑1**.
- **Chaîne clinique** : le cœur du modèle est une succession de relations **1‑à‑1** :
  `RDV → CONSULTATION → FACTURE`, avec `ORDONNANCE` optionnelle rattachée à la consultation.
- **`CONSULTATION ⟷ ACTE`** : relation **plusieurs‑à‑plusieurs**. Le montant d'une `FACTURE`
  est calculé à partir de la somme des tarifs des actes de sa consultation.
- **Révision de consultation** : relation **réflexive** sur `CONSULTATION`
  (`consultation_origine`) reliant une consultation de révision à sa consultation d'origine.
- **Dossier médical** : `VACCINATION`, `ANTECEDENT_ALLERGIE` et `ANTECEDENT_MALADIE` sont des
  **entités associatives** matérialisant les liens plusieurs‑à‑plusieurs entre `PATIENT` et
  respectivement `VACCIN`, `ALLERGIE` et `MALADIE`.
- **Mutuelle** : un patient est affilié à **au plus une** mutuelle (lien facultatif) ; une
  mutuelle regroupe plusieurs affiliés.

**Domaines de valeurs** — `USER.role` : `ADMIN` · `SECRETAIRE` · `DOCTEUR` · `PATIENT` ·
`RDV.statut` : `EN_ATTENTE` · `CONFIRME` · `ANNULE` · `TERMINE` · `FACTURE.statut_paiement` :
`NON_PAYE` · `PAYE` · `EN_ATTENTE` · `ANTECEDENT_ALLERGIE.intensite` : `Faible` · `Moyenne` · `Grave`.

## Prérequis

- [Docker](https://www.docker.com/) et Docker Compose installés.

---

## Installation et lancement

1. **Cloner le dépôt**

   ```bash
   git clone <url-du-depot>
   cd Projet-Si
   ```

2. **Construire et démarrer les conteneurs**

   ```bash
   docker compose up --build
   ```

   Au démarrage, le conteneur `web` exécute automatiquement (via `entrypoint.sh`) :
   - les migrations de la base de données ;
   - le remplissage de la base avec des données de test (`remplir_db`) ;
   - le serveur de développement Django.

3. **Ouvrir l'application** : [http://localhost:8000](http://localhost:8000)

---

## Comptes de test

Le script de remplissage crée automatiquement des comptes. **Le mot de passe est `123`
pour tous.**

| Rôle       | Identifiant(s)          |
|------------|-------------------------|
| Docteur    | `doc_0` … `doc_4`       |
| Secrétaire | `secretaire`            |
| Patient    | `patient_0` … `patient_19` |

Pour créer un compte **administrateur** (accès à `/admin/`) :

```bash
docker compose exec web python manage.py createsuperuser
```

> À chaque démarrage du conteneur, le script `remplir_db` **supprime et régénère**
> les rendez-vous, consultations et factures. Les données de test ne sont donc pas
> persistantes entre deux redémarrages.

---

## Commandes utiles

Toutes les commandes `manage.py` s'exécutent dans le conteneur `web` :

```bash
# Régénérer les données de test
docker compose exec web python manage.py remplir_db

# Créer un super-utilisateur
docker compose exec web python manage.py createsuperuser

# Arrêter les conteneurs
docker compose down

```

---

## Structure du projet

```
Projet-Si/
├── accounts/          # Utilisateurs, rôles, tableaux de bord, seed (remplir_db)
├── planning/          # Rendez-vous
├── consultations/     # Consultations, actes, ordonnances
├── facturation/       # Factures
├── dossiers/          # Dossier médical
├── django_project/    # Configuration Django (settings, urls)
├── templates/         # Templates HTML (base + par application)
├── static/            # Fichiers statiques
├── docker-compose.yml # Services web + db
├── Dockerfile         # Image de l'application
├── entrypoint.sh      # Migrations + seed + lancement du serveur
└── requirements.txt   # Dépendances Python
```

---
