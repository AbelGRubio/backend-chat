from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, \
    RequestResponseEndpoint
from starlette.responses import Response

from ..configuration import KEYCLOAK_OPENID


class AuthMiddleware(BaseHTTPMiddleware):
    """

    This code defines an AuthMiddleware class that extends BaseHTTPMiddleware
    to handle authentication for incoming HTTP requests. It checks if the
    request URL is in a predefined list of paths that do not require
    authentication. If the URL is not in this list, it verifies the
    presence of a valid API key in the request headers before allowing
    the request to proceed.

     """
    __jump_paths__ = ['/docs', '/openapi.json', '/redoc',
                      '/health', '/favicon.ico']

    __name__api_key__ = 'API_KEY'
    __auth__ = 'authorization'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def unauthorised(
            code: int = 401, msg: str = 'Unauthorised') -> JSONResponse:
        """
            Return a message of unauthorised
        """
        return JSONResponse(status_code=code, content=msg)

    def _is_jump_url_(self, request: Request) -> bool:
        return request.url.path in self.__jump_paths__

    def get_api_key(self, request: Request) -> str:
        return request.headers.get(self.__name__api_key__, '')

    def decode_token(self, token: str):
        token_ = token.replace('Bearer ', '')
        payload = KEYCLOAK_OPENID.decode_token(token_)
        return payload

    def get_header_token(self, request: Request):
        return request.headers.get(self.__auth__, '')

    def get_user_config(self, request: Request) -> dict | None:
        token = self.get_header_token(request)
        try:
            decode_token = self.decode_token(token)
            return decode_token
        except Exception:
            return None

    def is_auth(self, request: Request) -> dict | None:
        """
        queda por implementar
        :param request:
        :return:
        """
        return self.get_user_config(request)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
            The dispatch method in the AuthMiddleware class is an asynchronous
            middleware function that processes incoming HTTP requests.
            It checks if the request URL is in a predefined list of paths
            that do not require authentication. If the URL is not in this
            list, it verifies the presence of a valid API key in the request
            headers before allowing the request to proceed.
            :param request:  An instance of Request representing the incoming
            HTTP request.
            :param call_next: A callable (RequestResponseEndpoint) that processes
            the next middleware or the actual request handler
            :return: Returns a Response object, either from the next
            middleware/request handler or an unauthorized response.
        """
        if self._is_jump_url_(request):
            return await call_next(request)

        response = self.unauthorised()

        if self.is_auth(request):
            response = await call_next(request)

        return response
