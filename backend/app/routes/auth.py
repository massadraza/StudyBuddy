from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import database_models, schemas
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)

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

@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: database_models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


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
