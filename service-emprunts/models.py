from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey
from database import Base

class Emprunt(Base):
    """
    Représente la table 'emprunts' dans PostgreSQL.

    Chaque emprunt lie :
      - un utilisateur (utilisateur_id)  → qui a pris le livre
      - un livre      (livre_id)         → lequel
    Et enregistre :
      - date_emprunt  → quand il l'a pris
      - date_retour_prevue → quand il doit le rendre (par défaut +14 jours)
      - date_retour_reelle → quand il l'a effectivement rendu (null = pas encore rendu)
      - retard        → True si rendu après la date prévue
    """
    __tablename__ = "emprunts"

    id                  = Column(Integer, primary_key=True, index=True)
    utilisateur_id      = Column(Integer, nullable=False)   # référence vers service-utilisateurs
    livre_id            = Column(Integer, nullable=False)   # référence vers service-livres
    date_emprunt        = Column(Date, nullable=False)
    date_retour_prevue  = Column(Date, nullable=False)
    date_retour_reelle  = Column(Date, nullable=True)       # null = livre pas encore rendu
    retard              = Column(Boolean, default=False)
