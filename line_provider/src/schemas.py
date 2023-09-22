from pydantic import BaseModel, PositiveFloat, validator
from datetime import datetime
from typing import Optional
from src.models import EventState

class EventSchema(BaseModel):
    coefficient: PositiveFloat
    state:EventState

class EventUpdate(EventSchema):
    @validator('coefficient')
    def validate_coefficient_scale(cls, value):
        # Проверяем, что число имеет не более двух знаков после запятой
        if value %1< 0.99:
            return value
        raise ValueError('Coefficient must have at most 2 decimal places')


class EventCreate(EventSchema):
    deadline:Optional[datetime]=None
    @validator('coefficient')
    def validate_coefficient_scale(cls, value):
        # Проверяем, что число имеет не более двух знаков после запятой
        if value %1< 0.99:
            return value
        raise ValueError('Coefficient must have at most 2 decimal places')


class EventRead(EventCreate):
    event_id:int
    class Config:
        from_attributres=True