from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from src.env import ENV
from sqlalchemy.ext.declarative import declarative_base



BaseModel = declarative_base()

engine = create_async_engine(ENV.url_postgre, echo=False, future=True)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)