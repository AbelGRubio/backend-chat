from fastapi import WebSocket

from ..configuration import KEYCLOAK_OPENID, KEYCLOAK_ADMIN


class WebSocketAuthMiddleware:
    """
    Middleware personalizado para autenticación de WebSockets.
    No hereda de BaseHTTPMiddleware y está diseñado exclusivamente
    para manejar autenticación de WebSockets.
    """
    __auth__ = 'authorization'

    async def unauthorised(self, websocket: WebSocket, code: int = 1008,
                           msg: str = 'Unauthorised'):
        """
        Cierra la conexión WebSocket con un código de error 1008.
        """
        await websocket.close(code=code, reason=msg)

    def decode_token(self, token: str):
        """
        Decodifica el token JWT extraído de los headers del WebSocket.
        """
        token_ = token.replace('Bearer ', '')
        payload = KEYCLOAK_OPENID.decode_token(token_)
        return payload

    def is_auth(self, token: str) -> str:
        """
        Verifica si el WebSocket está autenticado a través del token JWT.
        """
        try:
            decode_token = self.decode_token(token)
            # Save username in header
            return decode_token
        except Exception as e:
            print(f"Autenticación fallida: {e}")
            return ''
