# SQL Database Schemas
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    has_study_guide = Column(Boolean, default=False, nullable=False)
    encrypted_openai_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    mastery_scores = relationship("MasteryScore", back_populates="user")
    practice_questions = relationship("PracticeQuestion", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"
    # Every user_id in conversations must match an existing id in users - gives it the unique identity characteristic
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "human" or "ai"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class MasteryScore(Base):
    __tablename__ = "mastery_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="mastery_scores")

    """

    This is the repeated work that is saved by using a relationship()

    scores = db.query(MasteryScore).filter(
        MasteryScore.user_id == user.id
    ).all()

    """

class PracticeQuestion(Base):
    __tablename__ = "practice_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    topic = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    answered_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="practice_questions")

    # relationship(NAME_OF_TABLE, NAME_OF_RELATIONSHIP_IN_TABLE)
