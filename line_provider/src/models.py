from collections.abc import Iterator
from datetime import datetime
from src.engine import BaseModel
from enum import Enum
from sqlalchemy import Column, Integer, DateTime, Enum as EnumSQL, NUMERIC, CheckConstraint

class EventState(Enum):
    NEW=1
    FINISHED_WIN=2
    FINISHED_LOSE=3

    def __str__(self):
        return str(self.value)
    def __iter__(self):
        return str(self.value)


class Event(BaseModel):
    __tablename__ ='event'
    event_id=Column(Integer, primary_key=True,nullable=False,unique=True)
    coefficient=Column(NUMERIC(scale=2),nullable=False)
    deadline = Column(DateTime, default=datetime.now )
    state=Column(EnumSQL(EventState), nullable=False)
    __table_args__ = (
        CheckConstraint(coefficient>=0, name='check_positive_coefficient'),
    )
    def __str__(self):
        return f"{self.event_id} {self.coefficient} {self.state}"
