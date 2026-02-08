from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.database import Base


class DivergenceSignal(Base):
    __tablename__ = "divergence_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(30), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Sentiment metrics
    sentiment_score_avg = Column(Float, nullable=True)
    discussion_volume = Column(Integer, nullable=True)
    sentiment_velocity = Column(Float, nullable=True)
    velocity_window_minutes = Column(Integer, nullable=True)

    # Divergence
    divergence_score = Column(Float, nullable=True)  # z-score based
    divergence_direction = Column(String(10), nullable=True)  # hype, panic, neutral

    # Confidence
    confidence_score = Column(Float, nullable=True)
    model_certainty = Column(Float, nullable=True)
    data_sufficiency = Column(Float, nullable=True)
    signal_consistency = Column(Float, nullable=True)

    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(10), nullable=False, default="test", index=True)  # test or live
