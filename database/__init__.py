# database/__init__.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建数据库引擎
engine = create_engine("sqlite:///knowledge.db", echo=True)

# 生成 SessionLocal
SessionLocal = sessionmaker(bind=engine)

# ✅ 加上这个函数！
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()