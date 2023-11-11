from datetime import datetime

from app.database import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped


class Message(Base):
    __tablename__ = "messages"

    id_: Mapped[int] = Column(Integer, primary_key=True)
    input_text: Mapped[str] = Column(String)
    result_prediction: Mapped[str] = Column(String)
    baseline_used: Mapped[str] = Column(String)
    execution_date: Mapped[datetime] = Column(DateTime)
