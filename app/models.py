from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .db import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    category = Column(String, nullable=True)
    is_purchased = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)