from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models.database_models import MasteryScore

def mastery_tracker_agent(
    user_id: int,
    topic: str,
    is_correct: bool,
    db: Session
) -> Dict[str, Any]:
    """Updates mastery scores based on student performance"""
    
    # Get or create mastery score
    mastery_score = db.query(MasteryScore).filter(
        MasteryScore.user_id == user_id,
        MasteryScore.topic == topic
    ).first()
    
    if not mastery_score:
        # Create new mastery score
        mastery_score = MasteryScore(
            user_id=user_id,
            topic=topic,
            score=0.5
        )
        db.add(mastery_score)
    
    current_score = mastery_score.score
    
    # Update score
    if is_correct:
        new_score = min(1.0, current_score + 0.1)
        print(f"[Mastery Tracker] ✅ {topic}: {current_score:.0%} → {new_score:.0%}")
    else:
        new_score = max(0.0, current_score - 0.15)
        print(f"[Mastery Tracker] ❌ {topic}: {current_score:.0%} → {new_score:.0%}")
    
    mastery_score.score = new_score
    db.commit()
    db.refresh(mastery_score)
    
    return {
        "topic": topic,
        "new_score": new_score,
        "old_score": current_score
    }
