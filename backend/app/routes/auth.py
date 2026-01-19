from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from openai import OpenAI
import httpx
from ..database import get_db
from ..models import database_models, schemas
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)
from ..encryption import encrypt_api_key, decrypt_api_key
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

"""
Using Dependency Injection --> Why would we use it?

First of all, what is a dependency?
- Anything that a route needs like a db session, auth, config val, cache

If we didn't have dependency injection 

EXAMPLE:

def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

WITH DEPENDENCY INJECTION

def get_users(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    return users

Creates and closes DB Sessions
"""

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(database_models.User).filter(
        database_models.User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = database_models.User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_current_user_info(current_user: database_models.User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "has_openai_key": current_user.encrypted_openai_key is not None,
        "created_at": current_user.created_at
    }


@router.post("/logout")
def logout(
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    """Logout and clear user's chat history"""
    # Get all conversations for this user
    conversations = db.query(database_models.Conversation).filter(
        database_models.Conversation.user_id == current_user.id
    ).all()

    # Delete all messages in those conversations
    for conversation in conversations:
        db.query(database_models.Message).filter(
            database_models.Message.conversation_id == conversation.id
        ).delete()

    # Delete all conversations
    db.query(database_models.Conversation).filter(
        database_models.Conversation.user_id == current_user.id
    ).delete()

    db.commit()

    return {"message": "Logged out successfully. Chat history cleared."}


@router.get("/api-key/status", response_model=schemas.ApiKeyStatus)
def get_api_key_status(current_user: database_models.User = Depends(get_current_user)):
    """Check if the user has set an OpenAI API key"""
    return {"has_api_key": current_user.encrypted_openai_key is not None}


@router.post("/api-key")
def set_api_key(
    request: schemas.ApiKeyRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set or update the user's OpenAI API key (validates before saving)"""
    api_key = request.api_key.strip()

    # Validate API key format
    if not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid API key format. OpenAI keys start with 'sk-'"
        )

    # Test the API key by making a simple API call
    try:
        client = OpenAI(api_key=api_key)
        # Use a minimal API call to validate the key
        client.models.list()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key: {str(e)}"
        )

    # Encrypt and save the API key
    encrypted_key = encrypt_api_key(api_key)
    current_user.encrypted_openai_key = encrypted_key
    db.commit()

    return {"message": "API key saved successfully"}


@router.delete("/api-key")
def delete_api_key(
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete the user's OpenAI API key"""
    current_user.encrypted_openai_key = None
    db.commit()

    return {"message": "API key deleted successfully"}


@router.post("/google", response_model=schemas.Token)
async def google_auth(request: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth token"""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google authentication is not configured"
        )

    # Verify the Google token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )

            google_data = response.json()

            # Verify the token was issued for our app
            if google_data.get("aud") != settings.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token was not issued for this application"
                )

            email = google_data.get("email")
            google_id = google_data.get("sub")
            full_name = google_data.get("name")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to verify Google token: {str(e)}"
        )

    # Check if user exists by Google ID or email
    user = db.query(database_models.User).filter(
        (database_models.User.google_id == google_id) |
        (database_models.User.email == email)
    ).first()

    if user:
        # Update Google ID if user exists but signed up with email/password
        if not user.google_id:
            user.google_id = google_id
            db.commit()
    else:
        # Create new user
        user = database_models.User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            hashed_password=None  # No password for Google OAuth users
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
