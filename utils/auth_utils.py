# utils/auth_utils.py

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import verify_token

# FastAPI 的依赖项：自动处理 Bearer Token 的提取
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> int:
    """
    从请求头中提取 token，验证并返回 user_id
    如果 token 无效或过期，将自动返回 401 错误
    """

    token = credentials.credentials  # 提取 Bearer 后面的那一串

    try:
        payload = verify_token(token)  # 解密 token
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Token 不包含 user_id")
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的身份凭证",
        )
