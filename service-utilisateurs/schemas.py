from pydantic import BaseModel, EmailStr
from typing import Optional
from models import TypeUtilisateur

class UtilisateurCreate(BaseModel):
    """Données attendues pour CRÉER un utilisateur."""
    nom:       str
    prenom:    str
    email:     str
    telephone: Optional[str] = None
    type:      TypeUtilisateur
    matricule: str

class UtilisateurUpdate(BaseModel):
    """Données pour MODIFIER un utilisateur (tous optionnels)."""
    nom:       Optional[str] = None
    prenom:    Optional[str] = None
    email:     Optional[str] = None
    telephone: Optional[str] = None
    type:      Optional[TypeUtilisateur] = None

class UtilisateurResponse(BaseModel):
    """Ce qu'on retourne à l'utilisateur."""
    id:        int
    nom:       str
    prenom:    str
    email:     str
    telephone: Optional[str]
    type:      TypeUtilisateur
    matricule: str

    class Config:
        from_attributes = True
