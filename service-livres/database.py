from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de connexion à PostgreSQL
# On lit les infos depuis les variables d'environnement (définies dans docker-compose)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/bibliotheque"
)

# Création du moteur de connexion
engine = create_engine(DATABASE_URL)

# Fabrique de sessions (une session = une conversation avec la BDD)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous nos modèles
Base = declarative_base()

# Fonction utilitaire pour obtenir une session BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
