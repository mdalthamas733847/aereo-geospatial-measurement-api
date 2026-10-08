from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    geometry_type = Column(String(50), nullable=False)
    feature_count = Column(Integer, nullable=False)
    area_sq_m = Column(Float, nullable=True)
    perimeter_m = Column(Float, nullable=True)
    length_m = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
