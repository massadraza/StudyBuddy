from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas (matches your TutorState)
class ChatMessage(BaseModel):
    role: str  # "human" or "ai"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: int
    retrieved_docs: List[str]  # Page content from docs

# Practice Schemas
class PracticeQuestionRequest(BaseModel):
    topic: Optional[str] = None  # Optional: focus on specific topic

class PracticeQuestionResponse(BaseModel):
    question_id: int
    question: str
    # Note: correct_answer NOT sent to frontend

class PracticeAnswerRequest(BaseModel):
    question_id: int
    student_answer: str

class PracticeAnswerResponse(BaseModel):
    is_correct: bool
    feedback: str
    correct_answer: str
    topic: str
    new_mastery_score: float

# Progress Schemas
class TopicMastery(BaseModel):
    topic: str
    score: float  # 0.0 to 1.0
    
class ProgressResponse(BaseModel):
    mastery_scores: List[TopicMastery]
