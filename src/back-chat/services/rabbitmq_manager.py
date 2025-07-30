import asyncio
from typing import Optional

from aio_pika import connect, Message, Channel, Queue
from aio_pika.exceptions import AMQPConnectionError


class RabbitMQManager:
    def __init__(self, rabbitmq_url: str, manager, max_retries: int = 3):
        """
        Clase para gestionar RabbitMQ con publicación, consumo y reconexión.

        :param rabbitmq_url: URL de conexión a RabbitMQ.
        :param manager: Instancia del gestor WebSocket para notificar clientes.
        :param max_retries: Número máximo de reintentos de conexión.
        """
        self.rabbitmq_url = rabbitmq_url
        self.manager = manager
        self.max_retries = max_retries
        self.connection = None
        self.channel: Optional[Channel] = None
        self.queue: Optional[Queue] = None

    async def connect(self) -> bool:
        """
        Conecta a RabbitMQ con reintentos.
        :return: True si la conexión fue exitosa, False en caso contrario.
        """
        for attempt in range(self.max_retries):
            try:
                self.connection = await connect(self.rabbitmq_url)
                self.channel = await self.connection.channel()
                return True
            except AMQPConnectionError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)  # Esperar antes de reintentar
        await self.manager.broadcast(
            "El servicio de actualización de alarmas en tiempo real "
            "no está disponible.")
        return False

    async def publish_message(self, queue_name: str, message: str):
        """
        Publica un mensaje en una cola de RabbitMQ.
        :param queue_name: Nombre de la cola.
        :param message: Mensaje a enviar.
        """
        if not self.channel:
            print("No RabbitMQ channel available. Attempting to reconnect...")
            if not await self.connect():
                return

        try:
            await self.channel.default_exchange.publish(
                Message(body=message.encode()),
                routing_key=queue_name,
            )
            print(f"Message published to {queue_name}: {message}")
        except Exception as e:
            print(f"Failed to publish message: {e}")

    async def publish_message_to_exchange(
            self, exchange_name: str, message: str, routing_key: str = ''):
        """
        Publica un mensaje en un exchange de RabbitMQ.
        :param exchange_name: Nombre del exchange.
        :param message: Mensaje a enviar.
        :param routing_key: Key para enrutar el mensaje.
        """
        if not self.channel:
            print("No RabbitMQ channel available. Attempting to reconnect...")
            if not await self.connect():
                return

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name, type='fanout')
            await exchange.publish(Message(
                body=message.encode()), routing_key=routing_key)
            print(f"Message published to exchange {exchange_name}: {message}")
        except Exception as e:
            print(f"Failed to publish message to exchange: {e}")

    async def consume_messages(self, queue_name: str):
        """
        Consume mensajes de RabbitMQ y los retransmite a los WebSockets.
        :param queue_name: Nombre de la cola a consumir.
        """
        if not self.channel:
            print("No RabbitMQ channel available. Attempting to reconnect...")
            if not await self.connect():
                return

        try:
            self.queue = await self.channel.declare_queue(queue_name,
                                                          durable=True)
            async for message in self.queue:
                async with message.process():
                    print(f"Received message: {message.body.decode()}")
                    await self.manager.broadcast(message.body.decode())
        except Exception as e:
            print(f"Failed to consume messages: {e}")
            await self.manager.broadcast(
                "El servicio de actualización de alarmas en tiempo "
                "real no está disponible.")

    async def consume_messages_from_exchange(self, exchange_name: str):
        """
        Consume mensajes de un exchange de RabbitMQ y los retransmite a los
        WebSockets.
        :param exchange_name: Nombre del exchange a consumir.
        """
        if not self.channel:
            print("No RabbitMQ channel available. Attempting to reconnect...")
            if not await self.connect():
                return

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name, type='fanout')
            queue = await self.channel.declare_queue('', exclusive=True)
            await queue.bind(exchange)
            async for message in queue:
                async with message.process():
                    await self.manager.broadcast(message.body.decode())
        except Exception as e:
            print(f"Failed to consume messages from exchange: {e}")
            await self.manager.broadcast(
                "El servicio de actualización de alarmas en "
                "tiempo real no está disponible.")
