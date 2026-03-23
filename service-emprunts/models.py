from sqlalchemy import Column, Integer, Date, Boolean
from database import Base


class Emprunt(Base):
    """
    Représente la table 'emprunts' dans PostgreSQL.
    Chaque ligne lie un membre à un livre pour une période donnée.
    - date_retour_reelle est null tant que le livre n'a pas été rendu
    - retard est True si le livre a été rendu après la date prévue
    """
    __tablename__ = "emprunts"

    id                 = Column(Integer, primary_key=True, index=True)
    utilisateur_id     = Column(Integer, nullable=False)  # ref. vers service-utilisateurs
    livre_id           = Column(Integer, nullable=False)  # ref. vers service-livres
    date_emprunt       = Column(Date, nullable=False)
    date_retour_prevue = Column(Date, nullable=False)
    date_retour_reelle = Column(Date, nullable=True)
    retard             = Column(Boolean, default=False)
