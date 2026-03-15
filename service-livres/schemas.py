from pydantic import BaseModel
from typing import Optional

class LivreCreate(BaseModel):
    """
    Données attendues quand on CRÉE un livre (envoyées par l'utilisateur).
    """
    titre:  str
    auteur: str
    isbn:   str
    annee:  Optional[int] = None
    genre:  Optional[str] = None

class LivreUpdate(BaseModel):
    """
    Données attendues quand on MODIFIE un livre (tous les champs sont optionnels).
    """
    titre:       Optional[str] = None
    auteur:      Optional[str] = None
    isbn:        Optional[str] = None
    annee:       Optional[int] = None
    genre:       Optional[str] = None
    disponible:  Optional[bool] = None

class LivreResponse(BaseModel):
    """
    Ce qu'on RENVOIE à l'utilisateur après une requête.
    """
    id:         int
    titre:      str
    auteur:     str
    isbn:       str
    annee:      Optional[int]
    genre:      Optional[str]
    disponible: bool

    class Config:
        from_attributes = True  # Permet la conversion depuis un objet SQLAlchemy
