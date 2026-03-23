from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from models import TypeUtilisateur

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservice Utilisateurs",
    description="API de gestion des membres - Bibliothèque DIT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/utilisateurs", response_model=List[schemas.UtilisateurResponse])
def lister_utilisateurs(db: Session = Depends(get_db)):
    """Retourne la liste de tous les membres."""
    return db.query(models.Utilisateur).all()


@app.get("/utilisateurs/type/{type_utilisateur}", response_model=List[schemas.UtilisateurResponse])
def lister_par_type(type_utilisateur: TypeUtilisateur, db: Session = Depends(get_db)):
    """Retourne les membres filtrés par type : etudiant, professeur ou personnel_administratif."""
    return db.query(models.Utilisateur).filter(
        models.Utilisateur.type == type_utilisateur
    ).all()


@app.get("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
def obtenir_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Retourne le profil complet d'un membre."""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur


@app.post("/utilisateurs", response_model=schemas.UtilisateurResponse, status_code=201)
def creer_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    """Inscrit un nouveau membre. L'email et le matricule doivent être uniques."""
    if db.query(models.Utilisateur).filter(models.Utilisateur.email == utilisateur.email).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    if db.query(models.Utilisateur).filter(models.Utilisateur.matricule == utilisateur.matricule).first():
        raise HTTPException(status_code=400, detail="Ce matricule est déjà utilisé")

    nouveau = models.Utilisateur(**utilisateur.model_dump())
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau


@app.put("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
def modifier_utilisateur(utilisateur_id: int, mise_a_jour: schemas.UtilisateurUpdate, db: Session = Depends(get_db)):
    """Modifie un membre existant. Seuls les champs fournis sont mis à jour."""
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


@app.get("/health")
def health_check():
    """Vérifie que le service est opérationnel."""
    return {"status": "ok", "service": "utilisateurs"}
