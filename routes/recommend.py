# routes/recommend.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from database.models import Card, UserCard, User
from utils.auth_utils import get_current_user
from recommend import get_today_cards
from database import get_db


router = APIRouter()

@router.get("/api/recommend")
def recommend(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # 获取当前用户
    user = db.query(User).filter_by(id=user_id).first()

    # 获取用户已学过的卡片 ID
    learned = db.query(UserCard.card_id).filter_by(user_id=user_id).all()
    learned_ids = [l[0] for l in learned]

    # 获取用户关注的主题
    preferred_categories = user.followed_categories or []

    # 查询推荐卡片（排除已学 + 按兴趣分类）
    cards = db.query(Card).filter(
        Card.is_active == True,
        ~Card.id.in_(learned_ids),
        Card.category.in_(preferred_categories)
    ).order_by(Card.category, Card.order_in_category).all()

    # 返回数据给前端
    return {
        "user_id": user.id,
        "username": user.username,
        "learned_count": user.learned_count or 0,
        "streak_days": user.streak_days or 0,
        "cards": [
            {"id": c.id, "title": c.title, "category": c.category}
            for c in cards
        ]
    }