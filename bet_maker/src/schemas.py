from pydantic import BaseModel, PositiveFloat, validator
from datetime import datetime
from typing import Optional
from src.models import BetState

class BetCreate(BaseModel):
    summ: PositiveFloat
    event_f_id:int


class BetRead(BetCreate):
    bet_id:int
    state:BetState
    class Config:
        from_attributres=True