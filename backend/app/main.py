from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import create_tables, engine
from .vectorstore import vector_manager
from .routes import auth, chat, practice, progress

# Create database tables on startup
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="StudyBuddy API",
    description="AI-powered multi-agent tutoring system with mastery tracking",
    version="1.0.0"
)

# Configure CORS
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

# Startup event - load vectorstore
@app.on_event("startup")
async def startup_event():
    """Load study guide on startup"""
    print("🚀 Starting StudyBuddy API...")
    print("📚 Loading study guide...")
    vector_manager.load_study_guide()
    print("✅ Study guide loaded and vectorized!")
    print("🎓 StudyBuddy API is ready!")

# Health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to StudyBuddy API",
        "version": "1.0.0",
        "status": "healthy"
    }

# API documentation available at /docs
