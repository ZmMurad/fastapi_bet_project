import asyncio
import logging
from aio_pika import IncomingMessage, Message
from src.env import ENV
from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from src.engine import Session, engine, BaseModel
from src.schemas import BetCreate, BetRead
import src.crud as sc
from sqlalchemy.ext.asyncio import AsyncSession
from src.rabbit.server import mq, connect_to_broker


app = FastAPI()


@app.on_event('startup')
async def start_app():
    channel = await connect_to_broker()
    mq.channel=channel
    asyncio.create_task(startup_event_listener())
    # async with engine.begin() as conn:
    #     # await conn.run_sync(BaseModel.metadata.drop_all)
    #     await conn.run_sync(BaseModel.metadata.create_all)

async def startup_event_listener():
    await mq.consume_queue(parse_message, ENV.QUEUE_BET)



async def get_db():
    sessionlocal = Session()
    try:
        yield sessionlocal
    finally:
        await sessionlocal.close()







@app.get('/events/', response_model=list[dict])
async def get_events(skip:int=0, limit:int=100, db:AsyncSession=Depends(get_db)):
    await mq.send(ENV.QUEUE_EVENT, {'task':'get_events'})
    await asyncio.sleep(1)
    return dict_out




@app.get('/bets/', response_model=list[BetRead])
async def get_bets(db:AsyncSession=Depends(get_db)):
    db_bets = await sc.get_bets(db)
    return db_bets


@app.post('/bets/', response_model=BetRead)
async def post_bet(bet:BetCreate,db:AsyncSession=Depends(get_db)):
    db_bet = await sc.post_bet(db, bet)
    if db_bet is not None:
        return db_bet
    raise HTTPException(status_code=400, detail={'message':'something went wrong'})




async def parse_message(msg:IncomingMessage):
    global dict_out
    logging.warning(f"RECEIVED {msg.routing_key} {msg.body}")
    msg_dict= mq.deserialize(msg.body)
    if msg_dict['task'] == 'new_event':
        await mq.send(ENV.QUEUE_EVENT,{'task':'get_events'})
        await mq.ack_message(msg)
    if msg_dict['task']=='send_events':
        dict_out=msg_dict['body']
        await mq.ack_message(msg)


dict_out=[]

if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, proxy_headers=True)