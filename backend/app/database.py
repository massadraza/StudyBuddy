from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models.database_models import Base

# Create database engine - creates a connection to the database
engine = create_engine(
    settings.database_url,
    connect_args= {"check_same_thread": False} if "sqlite" in settings.database_url else {} # SQLite Thread Protection
)

# Create session factory - session will be used and then discarded 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if not already created
def create_tables():
    Base.metadata.create_all(bind=engine)

# Creates and closes sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()