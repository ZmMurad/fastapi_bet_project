from sqlalchemy.exc import IntegrityError
from src.models import Bet
from src.schemas import BetCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_bets(db:AsyncSession):
    query = select(Bet)
    result = await db.execute(query)
    curr = result.scalars().all()
    return curr


async def post_bet(db:AsyncSession, bet:BetCreate):
    bet_create = Bet(summ= bet.summ, event_f_id=bet.event_f_id)
    try:
        async with db.begin() as tx:
            db.add(bet_create)
            await tx.commit()
        await db.refresh(bet_create)
        return bet_create
    except IntegrityError as e:
        db.rollback()
        raise e