from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import create_tables
from .routes import auth, chat, practice, progress, study_guide

# Define lifespan context manager
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup logic
    print("Starting StudyBuddy API...")

    # Initialize database tables
    print("Creating database tables...")
    create_tables()
    print("Database tables ready!")

    print("StudyBuddy API is ready!")
    print("Note: Users must upload their own study guide before using chat/practice features.")

    yield  # app starts serving requests here

    print("Shutting down StudyBuddy API...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="StudyBuddy API",
    description="AI-powered multi-agent tutoring system with mastery tracking",
    version="1.0.0",
    lifespan=app_lifespan
)

# Configure CORS -- Security Protocol
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(practice.router)
app.include_router(progress.router)
app.include_router(study_guide.router)

# Health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to StudyBuddy API",
        "version": "1.0.0",
        "status": "healthy"
    }