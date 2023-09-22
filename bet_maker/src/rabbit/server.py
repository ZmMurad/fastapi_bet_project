from datetime import datetime
import json
import logging
from time import sleep
from typing import Any
from uuid import uuid4
import aio_pika
from src.env import ENV
from enum import EnumMeta

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, EnumMeta):
            return obj.name
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

BROKER_CONNECTION = None
BROKER_CHANNEL = None

class BaseMQ:
    def __init__(self,channel:aio_pika.Channel=None):
        self.channel=channel

    @staticmethod
    def serialize(data:Any):
        return json.dumps(data,cls=EnumEncoder).encode()

    @staticmethod
    def deserialize(data:bytes):
        return json.loads(data)


class MessageQueue(BaseMQ):
    """Класс предазначен для работы по принципу publisher / subscriber."""
    async def send(self, queue_name: str, data: Any):
        """MQ-метод для отправки месседжа в один конец."""
        # Крафт месседджа.
        # Месседж - объект который получит другой сервис.
        message = aio_pika.Message(
            body=self.serialize(data),
            content_type="application/json",
            correlation_id=str(uuid4()),
        )
        logging.warning(f"SEND {queue_name} {message.body}")
        # Публикация сообщения в брокер используя дефолтную очередь.
        await self.channel.default_exchange.publish(message, queue_name)

    async def consume_queue(self, func, queue_name: str, auto_delete_queue: bool = False):
        """Прослушивание очереди брокера."""
        # Создание queues в рабите
        queue = await self.channel.declare_queue(queue_name, auto_delete=auto_delete_queue, durable=True)

        # Вроде как постоянное итерирование по очереди в ожидании месседжа.
        # Есть алтернативный вариант получения месседжа через queue.get(timeout=N)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logging.warning(f'Received message body: {message.body}')
                await func(message)

    async def ack_message(self,message):
        # Подтверждаем успешное получение сообщения
        await message.ack()

    async def nack_message(self,message):
        # Подтверждаем неуспешное получение сообщения и возвращаем его в очередь
        await message.nack()

async def connect_to_broker() -> aio_pika.Channel:
    """Подключение к брокеру и возвращат канал для работы с брокером."""
    global BROKER_CONNECTION
    global BROKER_CHANNEL

    retries = 0
    while not BROKER_CONNECTION:
        conn_str = ENV.rmq_url
        logging.warning(f"Trying to create connection to broker: {conn_str}")
        try:
            BROKER_CONNECTION = await aio_pika.connect_robust(conn_str)
            logging.warning(f"Connected to broker ({type(BROKER_CONNECTION)} ID {id(BROKER_CONNECTION)})")
        except Exception as e:
            retries += 1
            logging.warning(f"Can't connect to broker {retries} time({e.__class__.__name__}:{e}). Will retry in 5 seconds...")
            sleep(5)

    if not BROKER_CHANNEL:
        logging.warning("Trying to create channel to broker")
        BROKER_CHANNEL = await BROKER_CONNECTION.channel()
        logging.warning("Got a channel to broker")

    return BROKER_CHANNEL


mq = MessageQueue()