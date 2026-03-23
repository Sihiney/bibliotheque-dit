from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum


class TypeUtilisateur(str, enum.Enum):
    """Types de membres autorisés dans la bibliothèque."""
    ETUDIANT                = "etudiant"
    PROFESSEUR              = "professeur"
    PERSONNEL_ADMINISTRATIF = "personnel_administratif"


class Utilisateur(Base):
    """Représente la table 'utilisateurs' dans PostgreSQL."""
    __tablename__ = "utilisateurs"

    id        = Column(Integer, primary_key=True, index=True)
    nom       = Column(String(100), nullable=False)
    prenom    = Column(String(100), nullable=False)
    email     = Column(String(200), unique=True, nullable=False)
    telephone = Column(String(20))
    type      = Column(Enum(TypeUtilisateur), nullable=False)
    matricule = Column(String(50), unique=True, nullable=False)
