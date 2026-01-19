from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import database_models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress"])

# Depends()
# Runs those functions before the router function is executed

@router.get("", response_model=schemas.ProgressResponse)
def get_progress(
    current_user: database_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's mastery scores across all topics"""
      
    mastery_scores = db.query(database_models.MasteryScore).filter(
        database_models.MasteryScore.user_id == current_user.id
    ).order_by(database_models.MasteryScore.score.asc()).all()
    
    topic_masteries = [
        schemas.TopicMastery(topic=score.topic, score=score.score)
        for score in mastery_scores
    ]
    
    return {"mastery_scores": topic_masteries}
