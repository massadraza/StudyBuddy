from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import database_models, schemas
from ..auth import get_current_user
from ..vectorstore import vector_manager
from ..graph import tutor_graph
from ..encryption import decrypt_api_key
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Q&A mode: Ask questions and get tutoring responses"""

    # Check if user has set an OpenAI API key
    if not current_user.encrypted_openai_key:
        raise HTTPException(
            status_code=403,
            detail="Please set your OpenAI API key before using the chat feature"
        )

    # Check if user has uploaded a study guide
    if not current_user.has_study_guide:
        raise HTTPException(
            status_code=403,
            detail="Please upload a study guide before using the chat feature"
        )

    # Decrypt the API key
    openai_api_key = decrypt_api_key(current_user.encrypted_openai_key)

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

    # Get user's vectorstore
    vectorstore = vector_manager.get_user_vectorstore(current_user.id, openai_api_key)

    # Run the LangGraph workflow in Q&A mode
    result = tutor_graph.invoke({
        "mode": "qa",
        "question": request.question,
        "student_answer": None,
        "user_id": current_user.id,
        "vectorstore": vectorstore,
        "db": db,
        "openai_api_key": openai_api_key,
        "retrieved_docs": [],
        "current_topic": "",
        "generated_question": "",
        "correct_answer": "",
        "answer": "",
        "is_correct": False,
        "feedback": "",
        "new_mastery_score": 0.0,
        "chat_history": chat_history
    })

    # Save messages to database
    human_message = database_models.Message(
        conversation_id=conversation.id,
        role="human",
        content=request.question
    )
    ai_message = database_models.Message(
        conversation_id=conversation.id,
        role="ai",
        content=result["answer"]
    )

    db.add(human_message)
    db.add(ai_message)
    db.commit()

    # Extract doc contents for response
    retrieved_doc_contents = [doc.page_content for doc in result["retrieved_docs"]]

    return {
        "answer": result["answer"],
        "conversation_id": conversation.id,
        "retrieved_docs": retrieved_doc_contents
    }
