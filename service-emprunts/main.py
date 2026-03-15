from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
import httpx
import models, schemas
from database import engine, get_db
import os

# Crée les tables au démarrage
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservice Emprunts",
    description="API de gestion des emprunts - Bibliothèque DIT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs des autres microservices (lues depuis les variables d'environnement Docker)
SERVICE_LIVRES       = os.getenv("SERVICE_LIVRES_URL",       "http://service-livres:8001")
SERVICE_UTILISATEURS = os.getenv("SERVICE_UTILISATEURS_URL", "http://service-utilisateurs:8002")

# ─────────────────────────────────────────────
# Fonctions utilitaires : appels vers les autres services
# ─────────────────────────────────────────────

def verifier_utilisateur(utilisateur_id: int) -> dict:
    """
    Appelle le service-utilisateurs pour vérifier qu'un membre existe.
    Si le service est indisponible ou l'utilisateur introuvable → erreur.
    """
    try:
        response = httpx.get(f"{SERVICE_UTILISATEURS}/utilisateurs/{utilisateur_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Utilisateur {utilisateur_id} introuvable")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service utilisateurs indisponible")

def verifier_livre(livre_id: int) -> dict:
    """
    Appelle le service-livres pour vérifier qu'un livre existe et est disponible.
    """
    try:
        response = httpx.get(f"{SERVICE_LIVRES}/livres/{livre_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Livre {livre_id} introuvable")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")

def marquer_livre_indisponible(livre_id: int):
    """Met disponible=False sur le livre emprunté."""
    try:
        httpx.put(f"{SERVICE_LIVRES}/livres/{livre_id}", json={"disponible": False}, timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")

def marquer_livre_disponible(livre_id: int):
    """Remet disponible=True sur le livre rendu."""
    try:
        httpx.put(f"{SERVICE_LIVRES}/livres/{livre_id}", json={"disponible": True}, timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")

# ─────────────────────────────────────────────
# POST /emprunts — Emprunter un livre
# ─────────────────────────────────────────────
@app.post("/emprunts", response_model=schemas.EmpruntResponse, status_code=201)
def emprunter_livre(emprunt: schemas.EmpruntCreate, db: Session = Depends(get_db)):
    """
    Enregistre un emprunt de livre.
    Vérifie : utilisateur existe + livre existe + livre disponible.
    """
    # 1. Vérifier que l'utilisateur existe
    verifier_utilisateur(emprunt.utilisateur_id)

    # 2. Vérifier que le livre existe et est disponible
    livre = verifier_livre(emprunt.livre_id)
    if not livre.get("disponible"):
        raise HTTPException(status_code=400, detail="Ce livre est déjà emprunté")

    # 3. Calculer la date de retour prévue (aujourd'hui + 14 jours par défaut)
    aujourd_hui = date.today()
    date_retour = emprunt.date_retour_prevue or (aujourd_hui + timedelta(days=14))

    # 4. Créer l'enregistrement
    nouvel_emprunt = models.Emprunt(
        utilisateur_id     = emprunt.utilisateur_id,
        livre_id           = emprunt.livre_id,
        date_emprunt       = aujourd_hui,
        date_retour_prevue = date_retour,
    )
    db.add(nouvel_emprunt)

    # 5. Marquer le livre comme indisponible
    marquer_livre_indisponible(emprunt.livre_id)

    db.commit()
    db.refresh(nouvel_emprunt)
    return nouvel_emprunt

# ─────────────────────────────────────────────
# PUT /emprunts/{id}/retour — Retourner un livre
# ─────────────────────────────────────────────
@app.put("/emprunts/{emprunt_id}/retour", response_model=schemas.EmpruntResponse)
def retourner_livre(emprunt_id: int, db: Session = Depends(get_db)):
    """
    Enregistre le retour d'un livre.
    Détecte automatiquement si c'est un retard.
    """
    emprunt = db.query(models.Emprunt).filter(models.Emprunt.id == emprunt_id).first()
    if not emprunt:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")
    if emprunt.date_retour_reelle:
        raise HTTPException(status_code=400, detail="Ce livre a déjà été retourné")

    aujourd_hui = date.today()
    emprunt.date_retour_reelle = aujourd_hui

    # Détection automatique du retard
    emprunt.retard = aujourd_hui > emprunt.date_retour_prevue

    # Remettre le livre disponible
    marquer_livre_disponible(emprunt.livre_id)

    db.commit()
    db.refresh(emprunt)
    return emprunt

# ─────────────────────────────────────────────
# GET /emprunts — Historique complet
# ─────────────────────────────────────────────
@app.get("/emprunts", response_model=List[schemas.EmpruntResponse])
def historique_emprunts(db: Session = Depends(get_db)):
    """Retourne l'historique complet de tous les emprunts."""
    return db.query(models.Emprunt).all()

# ─────────────────────────────────────────────
# GET /emprunts/en-cours — Livres actuellement empruntés
# ─────────────────────────────────────────────
@app.get("/emprunts/en-cours", response_model=List[schemas.EmpruntResponse])
def emprunts_en_cours(db: Session = Depends(get_db)):
    """Retourne uniquement les emprunts non encore retournés."""
    return db.query(models.Emprunt).filter(
        models.Emprunt.date_retour_reelle == None
    ).all()

# ─────────────────────────────────────────────
# GET /emprunts/retards — Emprunts en retard
# ─────────────────────────────────────────────
@app.get("/emprunts/retards", response_model=List[schemas.EmpruntResponse])
def emprunts_en_retard(db: Session = Depends(get_db)):
    """
    Retourne les emprunts en retard :
    - soit déjà marqués retard (retournés en retard)
    - soit encore en cours mais date dépassée
    """
    aujourd_hui = date.today()
    return db.query(models.Emprunt).filter(
        (models.Emprunt.retard == True) |
        (
            (models.Emprunt.date_retour_reelle == None) &
            (models.Emprunt.date_retour_prevue < aujourd_hui)
        )
    ).all()

# ─────────────────────────────────────────────
# GET /emprunts/utilisateur/{id} — Historique d'un membre
# ─────────────────────────────────────────────
@app.get("/emprunts/utilisateur/{utilisateur_id}", response_model=List[schemas.EmpruntResponse])
def historique_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Retourne tous les emprunts d'un membre spécifique."""
    return db.query(models.Emprunt).filter(
        models.Emprunt.utilisateur_id == utilisateur_id
    ).all()

# ─────────────────────────────────────────────
# GET /health — Santé du service
# ─────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "emprunts"}
