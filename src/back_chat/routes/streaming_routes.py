from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from ..configuration import MANAGER, RABBITMQ_MANAGER, EXCHANGE_NAME
from ..descriptors import MessageType
from ..middleware.auth_websocket import WebSocketAuthMiddleware
from ..models import Message
from ..models.schemas import NotificationSchema, MessageSchema

ws_router = APIRouter()

websocket_auth = WebSocketAuthMiddleware()


@ws_router.websocket("/messages")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):

    client_id = websocket_auth.is_auth(token)
    if client_id == '':
        return websocket_auth.unauthorised(websocket)

    await MANAGER.connect(client_id, websocket)
    msg_ = MessageSchema(user_id=client_id)
    msg_.connection_msg()
    await MANAGER.broadcast(msg_.to_json())
    try:
        while True:
            data = await websocket.receive_text()
            message_data = MessageSchema.parse_raw(data)

            if message_data.mtype == MessageType.MESSAGE.value:
                Message.create(user_id=message_data.user_id,
                               content=message_data.content)
                await MANAGER.broadcast(message_data.to_json())
    except WebSocketDisconnect:
        MANAGER.disconnect(client_id)
        msg_ = MessageSchema(user_id=client_id)
        msg_.disconnection_msg()
        await MANAGER.broadcast(msg_.to_json())


@ws_router.websocket("/ws/signal/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await MANAGER.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await MANAGER.broadcast(data)
    except WebSocketDisconnect:
        MANAGER.disconnect(client_id)


@ws_router.get("/connected_users")
async def get_connected_users():
    users = MANAGER.get_connected_users()
    return {"connected_users": users}


@ws_router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):

    client_id = websocket_auth.is_auth(token)
    if client_id == '':
        return websocket_auth.unauthorised(websocket)
    ipp_ = websocket.client.host + str(websocket.client.port)
    name_connection = client_id + ipp_
    await MANAGER.connect(name_connection, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = NotificationSchema.parse_raw(data)
            print(message_data)
            # await RABBITMQ_MANAGER.publish_message_to_exchange(
            #         EXCHANGE_NAME, message_data.json())
    except WebSocketDisconnect:
        MANAGER.disconnect(name_connection)
