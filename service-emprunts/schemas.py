from pydantic import BaseModel
from typing import Optional
from datetime import date


class EmpruntCreate(BaseModel):
    """Données attendues à la création d'un emprunt."""
    utilisateur_id:     int
    livre_id:           int
    date_retour_prevue: Optional[date] = None  # Si absent, le backend applique +14 jours


class EmpruntResponse(BaseModel):
    """Structure retournée par l'API pour un emprunt."""
    id:                 int
    utilisateur_id:     int
    livre_id:           int
    date_emprunt:       date
    date_retour_prevue: date
    date_retour_reelle: Optional[date]
    retard:             bool

    class Config:
        from_attributes = True
