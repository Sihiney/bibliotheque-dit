from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
import httpx
import models, schemas
from database import engine, get_db
import os

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

# URLs des autres microservices, injectées par Docker Compose
SERVICE_LIVRES       = os.getenv("SERVICE_LIVRES_URL",       "http://service-livres:8001")
SERVICE_UTILISATEURS = os.getenv("SERVICE_UTILISATEURS_URL", "http://service-utilisateurs:8002")


# -- Fonctions utilitaires : appels inter-services --

def verifier_utilisateur(utilisateur_id: int) -> dict:
    """Vérifie qu'un membre existe dans le service-utilisateurs."""
    try:
        response = httpx.get(f"{SERVICE_UTILISATEURS}/utilisateurs/{utilisateur_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Utilisateur {utilisateur_id} introuvable")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service utilisateurs indisponible")


def verifier_livre(livre_id: int) -> dict:
    """Vérifie qu'un livre existe dans le service-livres et retourne ses données."""
    try:
        response = httpx.get(f"{SERVICE_LIVRES}/livres/{livre_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Livre {livre_id} introuvable")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")


def marquer_livre_indisponible(livre_id: int):
    """Passe le statut du livre à disponible=False après un emprunt."""
    try:
        httpx.put(f"{SERVICE_LIVRES}/livres/{livre_id}", json={"disponible": False}, timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")


def marquer_livre_disponible(livre_id: int):
    """Repasse le statut du livre à disponible=True après un retour."""
    try:
        httpx.put(f"{SERVICE_LIVRES}/livres/{livre_id}", json={"disponible": True}, timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service livres indisponible")


# -- Endpoints --

@app.post("/emprunts", response_model=schemas.EmpruntResponse, status_code=201)
def emprunter_livre(emprunt: schemas.EmpruntCreate, db: Session = Depends(get_db)):
    """
    Enregistre un emprunt. Vérifie que l'utilisateur existe, que le livre existe
    et qu'il est disponible. La date de retour est fixée à +14 jours par défaut.
    """
    verifier_utilisateur(emprunt.utilisateur_id)

    livre = verifier_livre(emprunt.livre_id)
    if not livre.get("disponible"):
        raise HTTPException(status_code=400, detail="Ce livre est déjà emprunté")

    aujourd_hui = date.today()
    date_retour = emprunt.date_retour_prevue or (aujourd_hui + timedelta(days=14))

    nouvel_emprunt = models.Emprunt(
        utilisateur_id     = emprunt.utilisateur_id,
        livre_id           = emprunt.livre_id,
        date_emprunt       = aujourd_hui,
        date_retour_prevue = date_retour,
    )
    db.add(nouvel_emprunt)
    marquer_livre_indisponible(emprunt.livre_id)
    db.commit()
    db.refresh(nouvel_emprunt)
    return nouvel_emprunt


@app.put("/emprunts/{emprunt_id}/retour", response_model=schemas.EmpruntResponse)
def retourner_livre(emprunt_id: int, db: Session = Depends(get_db)):
    """
    Enregistre le retour d'un livre et détecte automatiquement les retards.
    Le champ retard est mis à True si la date réelle dépasse la date prévue.
    """
    emprunt = db.query(models.Emprunt).filter(models.Emprunt.id == emprunt_id).first()
    if not emprunt:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")
    if emprunt.date_retour_reelle:
        raise HTTPException(status_code=400, detail="Ce livre a déjà été retourné")

    aujourd_hui = date.today()
    emprunt.date_retour_reelle = aujourd_hui
    emprunt.retard = aujourd_hui > emprunt.date_retour_prevue

    marquer_livre_disponible(emprunt.livre_id)
    db.commit()
    db.refresh(emprunt)
    return emprunt


@app.get("/emprunts", response_model=List[schemas.EmpruntResponse])
def historique_emprunts(db: Session = Depends(get_db)):
    """Retourne l'historique complet de tous les emprunts."""
    return db.query(models.Emprunt).all()


@app.get("/emprunts/en-cours", response_model=List[schemas.EmpruntResponse])
def emprunts_en_cours(db: Session = Depends(get_db)):
    """Retourne les emprunts dont le livre n'a pas encore été rendu."""
    return db.query(models.Emprunt).filter(
        models.Emprunt.date_retour_reelle == None
    ).all()


@app.get("/emprunts/retards", response_model=List[schemas.EmpruntResponse])
def emprunts_en_retard(db: Session = Depends(get_db)):
    """
    Retourne les emprunts en retard : livres déjà rendus en retard,
    ou livres encore en cours dont la date de retour est dépassée.
    """
    aujourd_hui = date.today()
    return db.query(models.Emprunt).filter(
        (models.Emprunt.retard == True) |
        (
            (models.Emprunt.date_retour_reelle == None) &
            (models.Emprunt.date_retour_prevue < aujourd_hui)
        )
    ).all()


@app.get("/emprunts/utilisateur/{utilisateur_id}", response_model=List[schemas.EmpruntResponse])
def historique_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Retourne tous les emprunts d'un membre donné."""
    return db.query(models.Emprunt).filter(
        models.Emprunt.utilisateur_id == utilisateur_id
    ).all()


@app.get("/health")
def health_check():
    """Vérifie que le service est opérationnel."""
    return {"status": "ok", "service": "emprunts"}
