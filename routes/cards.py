from fastapi import APIRouter
from database import SessionLocal
from database.models import Card

router = APIRouter()

@router.get("/api/cards")
def get_all_cards():
    db = SessionLocal()
    cards = db.query(Card).filter_by(is_active=True).all()
    return [{"id": c.id, "title": c.title, "tags": [c.category]} for c in cards]
