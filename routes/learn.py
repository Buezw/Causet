from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from database.models import Card, UserCard  # ✅ 修复这行
from utils.auth_utils import get_current_user

router = APIRouter()

class LearnInput(BaseModel):
    card_id: int

@router.post("/api/learn")
def mark_as_learned(
    data: LearnInput,
    user_id: int = Depends(get_current_user)
):
    db: Session = SessionLocal()

    # 防重复学习
    existing = db.query(UserCard).filter_by(user_id=user_id, card_id=data.card_id).first()
    if existing:
        return {"success": False, "message": "你已经学过这张卡了"}

    # ✅ 读取卡片信息
    card = db.query(Card).filter_by(id=data.card_id).first()
    if not card:
        return {"success": False, "message": "卡片不存在"}

    # ✅ 插入学习记录
    user_card = UserCard(
        user_id=user_id,
        card_id=card.id,
        category=card.category,  # ✅ 添加分类字段
        learned_at=datetime.utcnow()
    )
    db.add(user_card)
    db.commit()

    return {"success": True, "message": "学习记录已保存"}
