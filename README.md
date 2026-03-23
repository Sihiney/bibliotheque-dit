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

**Technologies :** FastAPI (Python) · PostgreSQL · Docker · Jenkins

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
| Vérification | Contrôle la présence des fichiers |
| Build Docker | Construit les 4 images |
| Arrêt ancienne version | Supprime les anciens conteneurs |
| Déploiement | Lance les nouveaux conteneurs |
| Vérification santé | Teste les endpoints `/health` |

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
| GET | `/utilisateurs` | Lister les membres |
| GET | `/utilisateurs/type/etudiant` | Filtrer par type |
| POST | `/utilisateurs` | Inscrire un membre |
| PUT | `/utilisateurs/{id}` | Modifier un profil |
| DELETE | `/utilisateurs/{id}` | Supprimer un membre |

### Service Emprunts (port 8003)
| Méthode | Endpoint | Action |
|---|---|---|
| POST | `/emprunts` | Emprunter un livre |
| PUT | `/emprunts/{id}/retour` | Retourner un livre |
| GET | `/emprunts/en-cours` | Emprunts en cours |
| GET | `/emprunts/retards` | Emprunts en retard |
| GET | `/emprunts/utilisateur/{id}` | Historique membre |
