from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.smart_recommender import get_smart_recommendation
import logging

log = logging.getLogger("LearningBuddy.recommend")

router = APIRouter()

@router.get("/smart/{user_name}")
def recommend_smart(
    user_name: str,
    top_n: int = Query(5, ge=1, le=20),
    interests: Optional[str] = Query(None, description="Comma separated interests, e.g. 'python,ai'")
):
    try:
        interests_list: List[str] = (
            [i.strip() for i in interests.split(",") if i.strip()]
            if interests else []
        )

        recs = get_smart_recommendation(
            user_identifier=user_name,
            top_n=top_n,
            interests_override=interests_list if interests_list else None,
        )

        return {
            "user": user_name,
            "interests": interests_list,
            "recommendation": recs
        }

    except Exception as e:
        log.exception("Smart recommender failed")
        raise HTTPException(status_code=500, detail=str(e))
