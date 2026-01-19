from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .routes import auth, chat, practice, progress, study_guide

# ADD THESE
from .database import engine
from .models.database_models import Base


# Define lifespan context manager
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup logic
    print("Starting StudyBuddy Application...")

    # ✅ AUTO CREATE TABLES
    Base.metadata.create_all(bind=engine)

    print("Database managed by Alembic migrations")
    print("StudyBuddy API is ready!")

    yield  # app starts serving requests here

    print("Shutting down StudyBuddy API...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="StudyBuddy API",
    description="Full Stack Application Powered by LangChain/LangGraph",
    version="1.1.1",
    lifespan=app_lifespan
)
