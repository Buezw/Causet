from datetime import datetime, timedelta
from jose import JWTError, jwt

# ✅ JWT 的加密密钥（必须保密）
# 你可以换成自己定义的复杂字符串
SECRET_KEY = "your-very-secret-key"
ALGORITHM = "HS256"  # 加密算法（HMAC SHA256）
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # token 有效时间：7天

# ✅ 生成 JWT Token（登录成功后用这个函数）
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    根据传入的数据生成 JWT token
    data: 要写入 token 的用户信息（一般只需要 user_id）
    expires_delta: 传入一个 timedelta 表示过期时间
    """
    to_encode = data.copy()  # 拷贝一份用户数据

    # 设置过期时间（默认 7 天）
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # 加入过期字段

    # 使用密钥 + 算法进行加密，返回一个字符串 token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ✅ 验证 JWT Token（用户每次请求时调用这个函数）
def verify_token(token: str):
    """
    验证 token 是否有效，并返回解密出的用户数据
    如果无效，抛出 JWTError 异常
    """
    try:
        # 解密 + 校验 token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 我们只需要 user_id 字段
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise JWTError("Token 中没有 user_id")

        return user_id

    except JWTError as e:
        # 如果 token 解密失败，返回 None
        print(f"❌ Token 验证失败：{e}")
        return None
