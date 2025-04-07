# main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routes.auth import router as auth_router
from routes.cards import router as cards_router
from routes.recommend import router as recommend_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ 首页：返回 HTML 模板，真正的数据靠 JS 调用 /api/recommend 获取
@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ✅ 登录页
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ 子路由
app.include_router(auth_router)
app.include_router(cards_router)
app.include_router(recommend_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
