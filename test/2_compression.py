import tempfile
import os
import zlib

from webob import Request, Response

from fruition.api.client.webservice.base import WebServiceAPIClientBase
from fruition.api.client.webservice.wrapper import WebServiceAPIClientWrapper
from fruition.api.server.webservice.base import WebServiceAPIServerBase
from fruition.api.server.webservice.handler import WebServiceAPIHandlerRegistry

from fruition.util.log import logger, DebugUnifiedLoggingContext
from fruition.util.helpers import Assertion, Pause, CompressedIterator

# random_contents = "\n".join([random_string() for i in range(10)])
random_contents = "a" * 128

class TestServer(WebServiceAPIServerBase):
    handlers = WebServiceAPIHandlerRegistry()

    @handlers.methods("GET")
    @handlers.compress()
    @handlers.path("^/inline$")
    def inline_compress(self, request: Request, response: Response) -> bytes:
        return random_contents.encode("utf-8")

    @handlers.methods("GET")
    @handlers.path("^/download$")
    @handlers.download()
    @handlers.compress()
    def download_test_file(self, request: Request, response: Response) -> str:
        fd, path = tempfile.mkstemp()
        os.close(fd)
        with open(path, "w") as fh:
            fh.write(random_contents)
        return path


def main() -> None:
    with DebugUnifiedLoggingContext():
        server = TestServer()
        server.configure(
            **{"server": {"driver": "werkzeug", "host": "0.0.0.0", "port": 8192}}
        )

        try:
            for client_class in [WebServiceAPIClientWrapper, WebServiceAPIClientBase]:
                if client_class is WebServiceAPIClientBase:
                    server.start()
                    Pause.milliseconds(100)
                client = client_class()
                client.configure(
                    client={"host": "127.0.0.1", "port": 8192},
                    server={"instance": server},
                )
                Assertion(Assertion.EQ)(client.get("inline").text, random_contents)
                path = client.download(
                    "GET", "download", directory=os.path.dirname(__file__)
                )
                Assertion(Assertion.EQ)(open(path, "r").read(), random_contents)
                os.remove(path)
        finally:
            server.stop()


if __name__ == "__main__":
    main()
