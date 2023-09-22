import logging as log
from os import environ


class Environment:



    # CHAT_ID_NOTIFICATION: str = str(environ.get(
    #     "CHAT_ID_NOTIFICATION", default= "-"
    # ))

    POSTGRE_HOST:str = str(environ.get("POSTGRES_HOST"))
    POSTGRE_PORT:str = str(environ.get("POSTGRES_PORT"))
    POSTGRE_USERNAME:str = str(environ.get("POSTGRES_USER"))
    POSTGRE_DB_NAME:str = str(environ.get("POSTGRES_DB"))
    POSTGRES_PASSWORD:str = str(environ.get("POSTGRES_PASSWORD"))
    RABBIT_PORT:str = str(environ.get('RABBIT_PORT'))
    RABBIT_HOST:str = str(environ.get('RABBIT_HOST'))
    QUEUE_BET:str = str(environ.get('QUEUE_BET'))
    QUEUE_EVENT:str = str(environ.get('QUEUE_EVENT'))

    url_postgre = f"postgresql+asyncpg://{POSTGRE_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRE_HOST}:{POSTGRE_PORT}/{POSTGRE_DB_NAME}"
    rmq_url = f"amqp://guest:guest@{RABBIT_HOST}:{RABBIT_PORT}/"


    LOGGING_LEVEL = 20

log.basicConfig(
    level=20,
    format='[%(asctime)s.%(msecs)03d] [%(levelname)-6s] [%(filename)-24s] : %(message)s',
    handlers=[
        log.StreamHandler(),
    ]
)





ENV = Environment()