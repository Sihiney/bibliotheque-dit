from pydantic import BaseModel
from typing import Optional


class LivreCreate(BaseModel):
    """Données attendues à la création d'un livre."""
    titre:  str
    auteur: str
    isbn:   str
    annee:  Optional[int] = None
    genre:  Optional[str] = None


class LivreUpdate(BaseModel):
    """Données pour la modification d'un livre. Tous les champs sont optionnels."""
    titre:      Optional[str] = None
    auteur:     Optional[str] = None
    isbn:       Optional[str] = None
    annee:      Optional[int] = None
    genre:      Optional[str] = None
    disponible: Optional[bool] = None


class LivreResponse(BaseModel):
    """Structure retournée par l'API pour un livre."""
    id:         int
    titre:      str
    auteur:     str
    isbn:       str
    annee:      Optional[int]
    genre:      Optional[str]
    disponible: bool

    class Config:
        from_attributes = True  # Permet la conversion depuis un objet SQLAlchemy
