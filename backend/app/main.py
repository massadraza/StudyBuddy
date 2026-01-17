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
    print("Starting StudyBuddy Application...")

    # Initialize database tables
    print("Creating database tables...")

    # Creates tables if they do not exist
    create_tables()

    print("Database tables ready!")
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

# Configure CORS -- Security Protocols
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"]
)

# Include routers 
app.include_router(auth.router) 
app.include_router(chat.router)
app.include_router(practice.router)
app.include_router(progress.router)
app.include_router(study_guide.router)

# Health check endpoint - local testing purposes
@app.get("/")
def read_root():
    return {
        "message": "Welcome to StudyBuddy API",
        "version": "1.0.0",
        "status": "healthy"
    }
