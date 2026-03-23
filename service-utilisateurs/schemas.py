from pydantic import BaseModel
from typing import Optional
from models import TypeUtilisateur


class UtilisateurCreate(BaseModel):
    """Données attendues à la création d'un membre."""
    nom:       str
    prenom:    str
    email:     str
    telephone: Optional[str] = None
    type:      TypeUtilisateur
    matricule: str


class UtilisateurUpdate(BaseModel):
    """Données pour la modification d'un membre. Tous les champs sont optionnels."""
    nom:       Optional[str] = None
    prenom:    Optional[str] = None
    email:     Optional[str] = None
    telephone: Optional[str] = None
    type:      Optional[TypeUtilisateur] = None


class UtilisateurResponse(BaseModel):
    """Structure retournée par l'API pour un membre."""
    id:        int
    nom:       str
    prenom:    str
    email:     str
    telephone: Optional[str]
    type:      TypeUtilisateur
    matricule: str

    class Config:
        from_attributes = True
