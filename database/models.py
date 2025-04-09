# database/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

Base = declarative_base()

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime, nullable=False)
    order_in_category = Column(Integer, nullable=True)  # ✅ 添加这一行
    
# 用户表：记录用户名和加密密码
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    followed_categories = Column(JSON, default=list)
    learned_count = Column(Integer, default=0)     # ✅ 新增
    streak_days = Column(Integer, default=0)       # ✅ 新增


# 用户卡片学习记录表：谁学了哪张卡片
class UserCard(Base):
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    category = Column(String, nullable=False)  # ✅ 冗余保存卡片分类
    learned_at = Column(DateTime, default=datetime.utcnow)

    card = relationship("Card", backref="user_cards")