from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .routes import auth, chat, practice, progress, study_guide


# Define lifespan context manager
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup logic
    print("Starting StudyBuddy Application...")
    print("StudyBuddy API is ready!")

    yield  # app starts serving requests here

    print("Shutting down StudyBuddy API...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="StudyBuddy API",
    description="Full Stack Application Powered by LangChain/LangGraph",
    version="1.2.1",
    lifespan=app_lifespan
)

# Configure CORS -- Security Protocols
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
