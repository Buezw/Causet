from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uvicorn
from recommend import get_today_cards  # 推荐逻辑函数
from database import SessionLocal
from database.models import Card



app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    db = SessionLocal()

    # 临时模拟“已学卡片”
    learned = {"牛顿第一定律"}

    recommended_cards = get_today_cards(db, learned)

    today_cards = [
        {
            "id": c.id,
            "title": c.title,
            "tags": [c.category]  # 也可以拓展为多个 tag
        }
        for c in recommended_cards
    ]

    return templates.TemplateResponse("homepage.html", {
        "request": request,
        "user_name": "小李",
        "today": datetime.now().strftime("%Y-%m-%d"),
        "today_cards": today_cards,
        "stats": {
            "total": len(learned),
            "streak": 6
        },
        "tags": list({c.category for c in recommended_cards})
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)