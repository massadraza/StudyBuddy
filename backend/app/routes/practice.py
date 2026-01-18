from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..database import get_db
from ..models import database_models, schemas
from ..auth import get_current_user
from ..vectorstore import vector_manager
from ..graph import tutor_graph
from ..encryption import decrypt_api_key


router = APIRouter(prefix="/practice", tags=["Practice"])

@router.post("/generate", response_model=schemas.PracticeQuestionResponse)
def generate_question(
    request: schemas.PracticeQuestionRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a practice question from the study guide"""

    # Check if user has set an OpenAI API key
    if not current_user.encrypted_openai_key:
        raise HTTPException(
            status_code=403,
            detail="Please set your OpenAI API key before using the practice feature"
        )

    # Check if user has uploaded a study guide
    if not current_user.has_study_guide:
        raise HTTPException(
            status_code=403,
            detail="Please upload a study guide before using the practice feature"
        )

    # Decrypt the API key
    openai_api_key = decrypt_api_key(current_user.encrypted_openai_key)

    # Get user's vectorstore
    vectorstore = vector_manager.get_user_vectorstore(current_user.id, openai_api_key)

    # Search query based on topic or general
    search_query = request.topic if request.topic else "Generate a practice question from study guide"

    # Run the LangGraph workflow in practice mode
    result = tutor_graph.invoke({
        "mode": "practice",
        "question": search_query,
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
        "chat_history": []
    })

    # Save practice question to database (without student answer yet)
    practice_question = database_models.PracticeQuestion(
        user_id=current_user.id,
        question=result["generated_question"],
        correct_answer=result["correct_answer"]
    )

    db.add(practice_question)
    db.commit()
    db.refresh(practice_question)

    return {
        "question_id": practice_question.id,
        "question": practice_question.question
    }

@router.post("/submit", response_model=schemas.PracticeAnswerResponse)
def submit_answer(
    request: schemas.PracticeAnswerRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit and evaluate a practice answer"""

    # Check if user has set an OpenAI API key
    if not current_user.encrypted_openai_key:
        raise HTTPException(
            status_code=403,
            detail="Please set your OpenAI API key before using the practice feature"
        )

    # Get the practice question
    practice_question = db.query(database_models.PracticeQuestion).filter(
        database_models.PracticeQuestion.id == request.question_id,
        database_models.PracticeQuestion.user_id == current_user.id
    ).first()

    if not practice_question:
        raise HTTPException(status_code=404, detail="Practice question not found")

    # Decrypt the API key
    openai_api_key = decrypt_api_key(current_user.encrypted_openai_key)

    # Get user's vectorstore
    vectorstore = vector_manager.get_user_vectorstore(current_user.id, openai_api_key)

    # Run the LangGraph workflow in evaluate mode
    result = tutor_graph.invoke({
        "mode": "evaluate",
        "question": practice_question.question,
        "student_answer": request.student_answer,
        "user_id": current_user.id,
        "vectorstore": vectorstore,
        "db": db,
        "openai_api_key": openai_api_key,
        "retrieved_docs": [],
        "current_topic": "",
        "generated_question": practice_question.question,
        "correct_answer": practice_question.correct_answer,
        "answer": "",
        "is_correct": False,
        "feedback": "",
        "new_mastery_score": 0.0,
        "chat_history": []
    })

    # Update practice question with student answer
    practice_question.student_answer = request.student_answer
    practice_question.is_correct = result["is_correct"]
    practice_question.topic = result["current_topic"]
    practice_question.answered_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "is_correct": result["is_correct"],
        "feedback": result["feedback"],
        "correct_answer": practice_question.correct_answer,
        "topic": result["current_topic"],
        "new_mastery_score": result["new_mastery_score"]
    }
