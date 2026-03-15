from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware   # ← doit être là
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from models import TypeUtilisateur

# Crée les tables au démarrage
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservice Livres",
    description="API de gestion des livres - Bibliothèque DIT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─────────────────────────────────────────────
# GET /utilisateurs — Lister tous les membres
# ─────────────────────────────────────────────
@app.get("/utilisateurs", response_model=List[schemas.UtilisateurResponse])
def lister_utilisateurs(db: Session = Depends(get_db)):
    """Retourne la liste de tous les membres de la bibliothèque."""
    return db.query(models.Utilisateur).all()

# ─────────────────────────────────────────────
# GET /utilisateurs/type/{type} — Filtrer par type
# ─────────────────────────────────────────────
@app.get("/utilisateurs/type/{type_utilisateur}", response_model=List[schemas.UtilisateurResponse])
def lister_par_type(type_utilisateur: TypeUtilisateur, db: Session = Depends(get_db)):
    """Liste les membres selon leur type : étudiant, professeur ou personnel."""
    return db.query(models.Utilisateur).filter(
        models.Utilisateur.type == type_utilisateur
    ).all()

# ─────────────────────────────────────────────
# GET /utilisateurs/{id} — Consulter un profil
# ─────────────────────────────────────────────
@app.get("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
def obtenir_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Retourne le profil complet d'un membre."""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur

# ─────────────────────────────────────────────
# POST /utilisateurs — Créer un membre
# ─────────────────────────────────────────────
@app.post("/utilisateurs", response_model=schemas.UtilisateurResponse, status_code=201)
def creer_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    """Inscrit un nouveau membre dans la bibliothèque."""
    # Vérifie que l'email n'est pas déjà utilisé
    if db.query(models.Utilisateur).filter(models.Utilisateur.email == utilisateur.email).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    # Vérifie que le matricule n'est pas déjà utilisé
    if db.query(models.Utilisateur).filter(models.Utilisateur.matricule == utilisateur.matricule).first():
        raise HTTPException(status_code=400, detail="Ce matricule est déjà utilisé")

    nouveau = models.Utilisateur(**utilisateur.model_dump())
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau

# ─────────────────────────────────────────────
# PUT /utilisateurs/{id} — Modifier un profil
# ─────────────────────────────────────────────
@app.put("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
def modifier_utilisateur(utilisateur_id: int, mise_a_jour: schemas.UtilisateurUpdate, db: Session = Depends(get_db)):
    """Modifie les informations d'un membre existant."""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    for champ, valeur in mise_a_jour.model_dump(exclude_unset=True).items():
        setattr(utilisateur, champ, valeur)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# ─────────────────────────────────────────────
# DELETE /utilisateurs/{id} — Supprimer un membre
# ─────────────────────────────────────────────
@app.delete("/utilisateurs/{utilisateur_id}", status_code=204)
def supprimer_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Supprime un membre de la bibliothèque."""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(utilisateur)
    db.commit()
    return None

# ─────────────────────────────────────────────
# GET /health — Santé du service
# ─────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "utilisateurs"}
