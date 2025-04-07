from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import SessionLocal
from database.models import User
from utils.hash import hash_password, verify_password
from utils.jwt import create_access_token  # ✅ 引入 JWT 工具

router = APIRouter()

class UserAuth(BaseModel):
    username: str
    password: str

# ✅ 注册接口
@router.post("/api/register")
def register(data: UserAuth):
    db = SessionLocal()

    # 检查是否已存在
    if db.query(User).filter_by(username=data.username).first():
        return JSONResponse(status_code=400, content={"success": False, "message": "用户名已存在"})

    # 创建新用户
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()

    return {"success": True, "message": "注册成功"}

# ✅ 登录接口：返回 JWT token
@router.post("/api/login")
def login(data: UserAuth):
    db = SessionLocal()

    # 查找用户
    user = db.query(User).filter_by(username=data.username).first()

    # 验证密码
    if not user or not verify_password(data.password, user.password_hash):
        return JSONResponse(status_code=401, content={"success": False, "message": "用户名或密码错误"})

    # 登录成功 → 生成 JWT token
    token = create_access_token({"user_id": user.id})

    # 返回给前端
    return {
        "success": True,
        "token": token,
        "message": "登录成功"
    }
