from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import database_models, schemas
from ..auth import get_current_user
from ..vectorstore import vector_manager
from ..agents.retriever import retriever_agent
from ..agents.question_generator import question_generator_agent
from ..agents.evaluator import evaluator_agent
from ..agents.topic_extractor import topic_extractor_agent
from ..agents.mastery_tracker import mastery_tracker_agent

router = APIRouter(prefix="/practice", tags=["Practice"])

@router.post("/generate", response_model=schemas.PracticeQuestionResponse)
def generate_question(
    request: schemas.PracticeQuestionRequest,
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a practice question from the study guide"""
    
    # Get vectorstore
    vectorstore = vector_manager.get_vectorstore()
    
    # Search query based on topic or general
    search_query = request.topic if request.topic else "Generate a practice question from study guide"
    
    # Run retriever agent
    retriever_result = retriever_agent(search_query, vectorstore)
    
    # Run question generator agent
    generator_result = question_generator_agent(retriever_result["retrieved_docs"])
    
    # Save practice question to database (without student answer yet)
    practice_question = database_models.PracticeQuestion(
        user_id=current_user.id,
        question=generator_result["generated_question"],
        correct_answer=generator_result["correct_answer"]
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
    
    # Get the practice question
    practice_question = db.query(database_models.PracticeQuestion).filter(
        database_models.PracticeQuestion.id == request.question_id,
        database_models.PracticeQuestion.user_id == current_user.id
    ).first()
    
    if not practice_question:
        raise HTTPException(status_code=404, detail="Practice question not found")
    
    # Get vectorstore for context
    vectorstore = vector_manager.get_vectorstore()
    retriever_result = retriever_agent(practice_question.question, vectorstore)
    
    # Run evaluator agent
    evaluator_result = evaluator_agent(
        generated_question=practice_question.question,
        correct_answer=practice_question.correct_answer,
        student_answer=request.student_answer,
        retrieved_docs=retriever_result["retrieved_docs"]
    )
    
    # Run topic extractor agent
    topic_result = topic_extractor_agent(
        question=practice_question.question,
        retrieved_docs=retriever_result["retrieved_docs"]
    )
    
    # Run mastery tracker agent (updates database)
    mastery_result = mastery_tracker_agent(
        user_id=current_user.id,
        topic=topic_result["current_topic"],
        is_correct=evaluator_result["is_correct"],
        db=db
    )
    
    # Update practice question with student answer
    practice_question.student_answer = request.student_answer
    practice_question.is_correct = evaluator_result["is_correct"]
    practice_question.topic = topic_result["current_topic"]
    from datetime import datetime
    practice_question.answered_at = datetime.utcnow()
    db.commit()
    
    return {
        "is_correct": evaluator_result["is_correct"],
        "feedback": evaluator_result["user_feedback"],
        "correct_answer": practice_question.correct_answer,
        "topic": topic_result["current_topic"],
        "new_mastery_score": mastery_result["new_score"]
    }
