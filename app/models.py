from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, func
from .database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # Unique + indexed so redirect lookups are O(log n) instead of a table scan
    short_code = Column(String(10), unique=True, index=True, nullable=False)
    original_url = Column(Text, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_accessed = Column(DateTime, nullable=True)
