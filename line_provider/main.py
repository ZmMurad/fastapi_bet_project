import logging
from aio_pika import IncomingMessage, Message
from src.env import ENV
from fastapi import Depends, FastAPI
import uvicorn
from src.engine import Session, engine, BaseModel
from src.schemas import EventCreate, EventRead, EventUpdate
import src.crud as sc
from sqlalchemy.ext.asyncio import AsyncSession
from src.rabbit.server import mq, connect_to_broker
import asyncio





app= FastAPI()

@app.on_event('startup')
async def init_tables():
    # await create_db_and_tables()
    channel = await connect_to_broker()
    mq.channel = channel
    asyncio.create_task(startup_event_listener())
    # async with engine.begin() as conn:
    #     await conn.run_sync(BaseModel.metadata.drop_all)
    #     await conn.run_sync(BaseModel.metadata.create_all)

async def startup_event_listener():
    await mq.consume_queue(parse_message, ENV.QUEUE_EVENT)



async def get_db():
    sessionlocal = Session()
    try:
        yield sessionlocal
    finally:
        await sessionlocal.close()


@app.get('/events/', response_model=list[EventRead])
async def get_events(skip:int=0, limit:int=100, db:AsyncSession=Depends(get_db)):
    db_events=await sc.get_events(db,skip,limit)
    return db_events


@app.post('/events/',response_model=EventRead)
async def post_event(event:EventCreate, db:AsyncSession=Depends(get_db)):
    db_event = await sc.add_event(db, event)
    if db_event is not None:
        msg={}
        msg['task'] = 'new_event'
        msg['body'] = EventRead(**db_event.__dict__).model_dump()
        await mq.send(ENV.QUEUE_BET, msg )
    return db_event

@app.put('/event/{event_id}/', response_model=EventRead)
async def change_event(event_id:int,event:EventUpdate, db:AsyncSession=Depends(get_db)):
    event_change = await sc.update_event(db, event_id, event)
    if event_change is not None:
        msg={}
        msg['task'] = 'new_event'
        msg['body'] = EventRead(**event_change.__dict__).model_dump()
        await mq.send(ENV.QUEUE_BET, msg )
    return event_change








async def parse_message(msg:IncomingMessage):
    logging.warning(f"RECEIVED {msg.routing_key} {msg.body}")
    msg_dict= mq.deserialize(msg.body)
    if msg_dict['task'] == 'get_events':
        db = Session()
        db_events = await sc.get_events_now(db)
        if db_events:
            msg_dict={}
            msg_dict['task'] = 'send_events'
            db_events = [EventRead(**db_event.__dict__).model_dump() for db_event in db_events]
            msg_dict['body'] = db_events
            await mq.ack_message(msg)
            await mq.send(ENV.QUEUE_BET,msg_dict)






if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, proxy_headers=True)