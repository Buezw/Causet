from fastapi import APIRouter, Depends, Request  # ✅ 加入 Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates   # ✅ 加入 Jinja2Templates
from sqlalchemy.orm import Session
from database.models import User
from utils.auth_utils import get_current_user
from database import get_db
from database.models import Card

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/preferences")
def get_preferences(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    return {"preferences": user.followed_categories or []}

@router.post("/api/preferences")
def set_preferences(preferences: list[str], user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    user.followed_categories = preferences
    db.commit()
    return {"success": True, "message": "关注主题已更新"}

@router.get("/preferences", response_class=HTMLResponse)
def preference_page(request: Request):  # ✅ 加入 Request 参数
    return templates.TemplateResponse("preferences.html", {"request": request})

@router.get("/api/categories")
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(Card.category).distinct().all()
    return [c[0] for c in categories]  # 从 (category,) 解包为字符串