from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, func
from app.core.database import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(30), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    delivery_volume = Column(BigInteger, nullable=True)
    delivery_pct = Column(Float, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(10), nullable=False, default="test", index=True)  # test or live
