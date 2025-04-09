from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal
from database.models import User, Card, UserCard  # ✅ 修复这行
from utils.auth_utils import get_current_user
from database import get_db
router = APIRouter()

class LearnInput(BaseModel):
    card_id: int

from datetime import datetime, timedelta

@router.post("/api/learn")
def learn_card(data: dict, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    card_id = data["card_id"]
    user = db.query(User).filter_by(id=user_id).first()
    card = db.query(Card).filter_by(id=card_id).first()

    existing = db.query(UserCard).filter_by(user_id=user_id, card_id=card_id).first()
    if existing:
        return {"success": False, "message": "已经学过这张卡片了"}

    # ✅ 插入学习记录
    uc = UserCard(user_id=user_id, card_id=card_id, category=card.category, learned_at=datetime.utcnow())
    db.add(uc)

    # ✅ 更新用户数据
    user.learned_count += 1

    # 连续学习判断逻辑（是否是昨天也学了）
    last = db.query(UserCard).filter_by(user_id=user_id).order_by(UserCard.learned_at.desc()).offset(1).first()
    if last:
        delta = datetime.utcnow().date() - last.learned_at.date()
        if delta == timedelta(days=1):
            user.streak_days += 1
        elif delta > timedelta(days=1):
            user.streak_days = 1
    else:
        user.streak_days = 1  # 首次学习

    db.commit()
    return {"success": True, "message": "学习记录已保存"}

