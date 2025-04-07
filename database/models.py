# database/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime, nullable=False)
    order_in_category = Column(Integer, nullable=True)
