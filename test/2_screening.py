import socket

from fruition.api.exceptions import AuthenticationError

from fruition.api.server.webservice.base import WebServiceAPIServerBase
from fruition.api.server.webservice.handler import WebServiceAPIHandlerRegistry
from fruition.api.client.webservice.base import WebServiceAPIClientBase
from fruition.api.middleware.webservice.screening import (
    ScreeningWebServiceAPIMiddleware,
)
from fruition.util.log import DebugUnifiedLoggingContext
from fruition.util.helpers import expect_exception

PORT = 9091


class ScreeningWebServer(ScreeningWebServiceAPIMiddleware, WebServiceAPIServerBase):
    handlers = WebServiceAPIHandlerRegistry()

    @handlers.path("/")
    @handlers.methods("GET")
    def emptyHandler(self, request, response):
        return


class ScreeningWebClient(ScreeningWebServiceAPIMiddleware, WebServiceAPIClientBase):
    pass


def main():
    with DebugUnifiedLoggingContext():
        server = ScreeningWebServer()
        try:
            server.configure(
                **{
                    "server": {
                        "host": "0.0.0.0",
                        "port": PORT,
                        "driver": "werkzeug",
                        "allowlist": [],
                        "offlist": "reject",
                    }
                }
            )
            server.start()
            client = ScreeningWebClient()
            client.configure(**{"client": {"host": "127.0.0.1", "port": PORT}})
            expect_exception(AuthenticationError)(lambda: client.get())
            server.stop()
            server.configure(
                **{
                    "server": {
                        "allowlist": [
                            "127.0.0.1",
                            socket.gethostbyname(socket.gethostname()),
                        ]
                    }
                }
            )
            server.start()
            client.get()
        finally:
            server.stop()


if __name__ == "__main__":
    main()
