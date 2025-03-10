from sqlalchemy import Column, String, Float, DateTime
from .database import Base
from datetime import datetime

class Blacklist(Base):
    __tablename__ = "blacklist"
    user_id = Column(String, primary_key=True)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True)
    user_id = Column(String)
    order_time = Column(DateTime)
    amount = Column(Float)
    order_status = Column(String)

class Rules(Base):
    __tablename__ = "rules"
    rule_id = Column(String, primary_key=True)
    rule_sql = Column(String)
    rule_reason = Column(String)