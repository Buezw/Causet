# routes/recommend.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from database.models import Card, UserCard, User
from utils.auth_utils import get_current_user
from recommend import get_today_cards


router = APIRouter()

@router.get("/api/recommend")
def api_recommend(user_id: int = Depends(get_current_user)):
    db: Session = SessionLocal()

    # ✅ 查询用户对象
    user = db.query(User).filter_by(id=user_id).first()
    username = user.username if user else f"ID:{user_id}"

    # 学过的卡片
    learned = db.query(UserCard).filter_by(user_id=user_id).all()
    learned_titles = {uc.card.title for uc in learned if uc.card}

    recommended = get_today_cards(db, learned_titles)

    return {
        "user_id": user_id,
        "username": username,  # ✅ 返回用户名
        "cards": [
            {"id": c.id, "title": c.title, "category": c.category}
            for c in recommended
        ]
    }
