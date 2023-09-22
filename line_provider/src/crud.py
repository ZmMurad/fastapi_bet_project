import logging
from sqlalchemy.exc import IntegrityError
from src.models import Event
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import EventCreate, EventRead, EventSchema, EventUpdate
from datetime import datetime



async def get_events(db:AsyncSession, skip:int = 0 , limit:int=100):
    query=select(Event).offset(skip).limit(limit)
    result = await db.execute(query)
    curr = result.scalars()
    return curr

async def get_events_now(db:AsyncSession):
    query=select(Event).where(Event.deadline>datetime.now())
    result = await db.execute(query)
    curr = result.scalars().all()
    return curr


async def add_event(db:AsyncSession,event:EventCreate):
    if event.deadline:
        event.deadline= event.deadline.replace(tzinfo=None)
    event_create = Event(coefficient = event.coefficient, deadline = event.deadline, state=event.state)
    try:
        async with db.begin() as tx:
            db.add(event_create)
            await tx.commit()
        await db.refresh(event_create)
        return event_create
    except IntegrityError as e:
        db.rollback()
        raise e

async def update_event(db:AsyncSession, event_id:int , event_update:EventUpdate):
    event = await db.get(Event, event_id)
    if event is None:
        return None
    event.coefficient=event_update.coefficient
    event.state=event_update.state
    try:
        await db.commit()
        await db.refresh(event)
        return event
    except IntegrityError as e:
        db.rollback()
        raise e

async def get_event_by_id(db:AsyncSession, event_id:int):
    event = await db.get(Event, event_id)
    return event