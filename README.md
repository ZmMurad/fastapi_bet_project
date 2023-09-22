## Развертывание сервисов поставщик информации и bet maker на FastAPI с применением RabbitMQ
### Технологии:
- FastAPI
- RabbitMQ(aiopika)
- Docker
- Docker-compose

#### О сервисах
- line_provider (поставщик информации)
- bet_maker (сервис ставок)
- Rabbit (Брокер сообщений)

Также каждый из сервисов поддерживает RESTApi за счет FastApi.

### Развертывание
- Перед началом вам нужно создать файл .env и добавить туда данные из env.example
- docker-compose up -d --build