# routes/recommend.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from database.models import Card, UserCard
from utils.auth_utils import get_current_user
from recommend import get_today_cards

router = APIRouter()

@router.get("/api/recommend")
def api_recommend(user_id: int = Depends(get_current_user)):
    db: Session = SessionLocal()

    # 查询该用户已学过的卡片
    learned = db.query(UserCard).filter_by(user_id=user_id).all()
    learned_titles = {uc.card.title for uc in learned if uc.card}

    # 推荐卡片
    recommended = get_today_cards(db, learned_titles)

    return [
        {"id": c.id, "title": c.title, "tags": [c.category]}
        for c in recommended
    ]
