# Bibliothèque Numérique - DIT

Plateforme de gestion de bibliothèque académique basée sur une architecture microservices.

Projet DevOps - Master 1 Intelligence Artificielle - Dakar Institute of Technology

**Groupe 2 :**
- AHOGA Josias
- BAH Mamoudou
- BAMBA Yannick
- DIOP Seynabou

---

## Architecture

```
├── service-livres/         -> API Livres        (port 8001)
├── service-utilisateurs/   -> API Utilisateurs  (port 8002)
├── service-emprunts/       -> API Emprunts      (port 8003)
├── frontend/               -> Interface web     (port 80)
├── docker-compose.yml      -> Orchestration
└── Jenkinsfile             -> Pipeline CI/CD
```

**Technologies :** FastAPI (Python) · PostgreSQL · Docker · Jenkins · Vue.js 3

---

## Fonctionnalités

### Authentification et rôles
- **Inscription** avec confirmation du mot de passe
- **Trois types d'utilisateurs** : Étudiant, Enseignant, Personnel administratif
- **Deux rôles** : Administrateur et Membre
- **Matricule étudiant** au format `NE202509001` (NE + année + mois + 3 chiffres)
- **Création de comptes par l'admin** avec email et mot de passe temporaire

### Dashboard adapté au rôle
- **Administrateur** : statistiques globales (livres, membres, emprunts en cours, retards), accès rapide aux différentes sections, activités récentes. Les cartes de statistiques sont cliquables et redirigent vers la liste détaillée correspondante.
- **Étudiant / Enseignant** : uniquement ses propres emprunts en cours, ses retards, et la liste des livres disponibles avec recherche.

### Sidebar
- Affiche sous le nom de l'utilisateur son rôle contextualisé : « Étudiant DIT », « Enseignant DIT » ou « Administrateur DIT »
- Le lien « Utilisateurs » n'apparaît que pour l'administrateur

### Gestion des livres
- Catalogue complet avec recherche par titre, auteur ou ISBN
- Ajout, modification et suppression (admin uniquement)
- Statut de disponibilité en temps réel

### Gestion des emprunts
- Formulaire d'emprunt avec sélection par liste déroulante (membre + livre disponible)
- Enregistrement du retour avec détection automatique des retards
- Calcul du nombre de jours de retard affiché dans la section Retards
- Après un emprunt ou un retour, la disponibilité des livres est mise à jour automatiquement

### Page d'accueil
- Design unifié : formulaire de connexion/inscription centré sur fond vert DIT (pas de split-screen)

---

## Lancement avec Docker Compose

### Prérequis
- Docker Desktop installé et démarré
- Git installé

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/Sihiney/bibliotheque-dit.git
cd bibliotheque-dit

# 2. Lancer toute l'application
docker compose up --build

# 3. Ouvrir dans le navigateur
# → Interface : http://localhost
# → API Livres : http://localhost:8001/docs
# → API Utilisateurs : http://localhost:8002/docs
# → API Emprunts : http://localhost:8003/docs
```

### Arrêter l'application

```bash
docker compose down
```

---

## Compte administrateur par défaut

Au premier lancement, il n'y a aucun compte. Pour créer un administrateur, utilisez l'API directement :

```bash
curl -X POST http://localhost:8002/utilisateurs \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Admin",
    "prenom": "DIT",
    "email": "admin@dit.sn",
    "mot_de_passe": "admin123",
    "type": "personnel_administratif",
    "role": "admin"
  }'
```

Ensuite, connectez-vous avec `admin@dit.sn` / `admin123` sur l'interface.

---

## Documentation des APIs

FastAPI génère automatiquement une documentation interactive.

| Service | URL de la doc |
|---|---|
| Livres | http://localhost:8001/docs |
| Utilisateurs | http://localhost:8002/docs |
| Emprunts | http://localhost:8003/docs |

---

## Pipeline Jenkins

### Prérequis Jenkins
- Jenkins installé avec les plugins : Git, Docker Pipeline

### Configuration

1. Créer un nouveau job Jenkins de type **Pipeline**
2. Dans **Pipeline > Definition**, choisir **Pipeline script from SCM**
3. Renseigner l'URL GitHub du projet
4. Jenkins utilisera automatiquement le `Jenkinsfile` à la racine

### Étapes du pipeline

| Étape | Description |
|---|---|
| Récupération du code | Clone le dépôt GitHub |
| Vérification de la structure | Contrôle la présence des fichiers |
| Build Docker | Construit les 4 images |
| Arrêt ancienne version | Supprime les anciens conteneurs |
| Déploiement | Lance les nouveaux conteneurs |
| Vérification santé | Teste les endpoints `/health` |
| Tests fonctionnels | Valide les APIs avec des requêtes POST et GET |

---

## Microservices

### Service Livres (port 8001)
| Méthode | Endpoint | Action |
|---|---|---|
| GET | `/livres` | Lister tous les livres |
| GET | `/livres/recherche?titre=...` | Rechercher |
| POST | `/livres` | Ajouter un livre |
| PUT | `/livres/{id}` | Modifier un livre |
| DELETE | `/livres/{id}` | Supprimer un livre |

### Service Utilisateurs (port 8002)
| Méthode | Endpoint | Action |
|---|---|---|
| POST | `/auth/register` | Inscription (avec confirmation mdp) |
| POST | `/auth/login` | Connexion |
| GET | `/auth/me` | Profil connecté |
| GET | `/utilisateurs` | Lister les membres |
| GET | `/utilisateurs/type/etudiant` | Filtrer par type |
| POST | `/utilisateurs` | Créer un membre (admin, avec mdp temporaire) |
| PUT | `/utilisateurs/{id}` | Modifier un profil |
| DELETE | `/utilisateurs/{id}` | Supprimer un membre |

### Service Emprunts (port 8003)
| Méthode | Endpoint | Action |
|---|---|---|
| POST | `/emprunts` | Emprunter un livre |
| PUT | `/emprunts/{id}/retour` | Retourner un livre |
| GET | `/emprunts/en-cours` | Emprunts en cours |
| GET | `/emprunts/retards` | Emprunts en retard |
| GET | `/emprunts/utilisateur/{id}` | Historique d'un membre |
