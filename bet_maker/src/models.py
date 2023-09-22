from src.engine import BaseModel
from enum import Enum
from sqlalchemy import Column, Integer, Enum as EnumSQL, NUMERIC, CheckConstraint


class BetState(Enum):
    NEW=1
    FINISHED_WIN=2
    FINISHED_LOSE=3
    def __str__(self):
        return str(self.value)


class Bet(BaseModel):
    __tablename__ ='bet'
    bet_id=Column(Integer, primary_key=True,nullable=False,unique=True)
    summ=Column(NUMERIC(scale=2),nullable=False)
    event_f_id = Column(Integer, nullable=False)
    state=Column(EnumSQL(BetState), nullable=False, default=BetState.NEW)
    __table_args__ = (
        CheckConstraint(summ>=0, name='check_positive_summ'),
    )
    def __str__(self):
        return f"{self.bet_id} {self.summ} {self.state} {self.event_f_id}"
