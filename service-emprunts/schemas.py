from pydantic import BaseModel
from typing import Optional
from datetime import date

class EmpruntCreate(BaseModel):
    """Données pour CRÉER un emprunt (emprunter un livre)."""
    utilisateur_id:     int
    livre_id:           int
    date_retour_prevue: Optional[date] = None  # Si absent → +14 jours automatiquement

class EmpruntResponse(BaseModel):
    """Ce qu'on retourne après une opération sur un emprunt."""
    id:                 int
    utilisateur_id:     int
    livre_id:           int
    date_emprunt:       date
    date_retour_prevue: date
    date_retour_reelle: Optional[date]
    retard:             bool

    class Config:
        from_attributes = True
