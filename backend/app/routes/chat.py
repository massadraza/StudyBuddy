from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import database_models, schemas
from ..auth import get_current_user
from ..vectorstore import vector_manager
from ..agents.retriever import retriever_agent
from ..agents.tutor import tutor_agent
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Q&A mode: Ask questions and get tutoring responses"""
    
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(database_models.Conversation).filter(
            database_models.Conversation.id == request.conversation_id,
            database_models.Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = database_models.Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Get chat history
    messages = db.query(database_models.Message).filter(
        database_models.Message.conversation_id == conversation.id
    ).order_by(database_models.Message.timestamp).all()
    
    chat_history = []
    for msg in messages:
        if msg.role == "human":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))
    
    # Get vectorstore
    vectorstore = vector_manager.get_vectorstore()
    
    # Run retriever agent
    retriever_result = retriever_agent(request.question, vectorstore)
    
    # Run tutor agent
    tutor_result = tutor_agent(
        question=request.question,
        retrieved_docs=retriever_result["retrieved_docs"],
        chat_history=chat_history
    )
    
    # Save messages to database
    human_message = database_models.Message(
        conversation_id=conversation.id,
        role="human",
        content=request.question
    )
    ai_message = database_models.Message(
        conversation_id=conversation.id,
        role="ai",
        content=tutor_result["answer"]
    )
    
    db.add(human_message)
    db.add(ai_message)
    db.commit()
    
    # Extract doc contents for response
    retrieved_doc_contents = [doc.page_content for doc in retriever_result["retrieved_docs"]]
    
    return {
        "answer": tutor_result["answer"],
        "conversation_id": conversation.id,
        "retrieved_docs": retrieved_doc_contents
    }
