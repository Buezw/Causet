from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.auth import router as auth_router
from routes.cards import router as cards_router
from routes.recommend import router as recommend_router

from database import SessionLocal
from database.models import UserCard
from recommend import get_today_cards
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 首页：支持带 user_id 参数展示推荐卡片
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, user_id: int = Query(...)):
    db = SessionLocal()

    # 查询用户已学过的卡片
    learned = db.query(UserCard).filter_by(user_id=user_id).all()
    learned_titles = {uc.card.title for uc in learned if uc.card}

    # 推荐卡片
    recommended_cards = get_today_cards(db, learned_titles)

    # 构造传给模板的数据结构
    today_cards = [
        {"id": c.id, "title": c.title, "tags": [c.category]}
        for c in recommended_cards
    ]

    return templates.TemplateResponse("homepage.html", {
        "request": request,
        "user_name": f"用户 {user_id}",
        "today": datetime.now().strftime("%Y-%m-%d"),
        "today_cards": today_cards,
        "stats": {
            "total": len(learned_titles),
            "streak": 6  # 示例，后续可接入真实 streak
        },
        "tags": list({c.category for c in recommended_cards})
    })

# 注册子路由模块
app.include_router(auth_router)
app.include_router(cards_router)
app.include_router(recommend_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
