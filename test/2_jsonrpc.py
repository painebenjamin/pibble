from pibble.api.server.webservice.rpc.jsonrpc import JSONRPCServer
from pibble.api.client.webservice.rpc.jsonrpc import JSONRPCClient
from pibble.api.client.webservice.wrapper import WebServiceAPIClientWrapper

from pibble.util.log import DebugUnifiedLoggingContext
from pibble.util.helpers import Assertion


class JSONRPCClientWrapper(JSONRPCClient, WebServiceAPIClientWrapper):
    pass


server = JSONRPCServer()


@server.register
@server.sign_request(int, int)
@server.sign_response(int)
def add(a: int, b: int) -> int:
    """
    Adds two numbers together.
    """
    return a + b


@server.register
@server.sign_named_request(base=int, exponent=2)
@server.sign_named_response(result=int)
def pow(base: int, exponent: int = 2) -> dict[str, int]:
    """
    Raises base to the power of exponent.
    """
    return {"result": base**exponent}


def main() -> None:
    with DebugUnifiedLoggingContext():
        server.configure(
            **{"server": {"driver": "werkzeug", "host": "0.0.0.0", "port": 8192}}
        )
        server.start()

        try:
            for client_class in [JSONRPCClientWrapper, JSONRPCClient]:
                client = client_class()
                client.configure(
                    **{
                        "client": {"host": "127.0.0.1", "port": 8192},
                        "server": {"instance": server},
                    }
                )
                Assertion(Assertion.EQ)(
                    client["system.listMethods"](),
                    [
                        "system.listMethods",
                        "system.methodSignature",
                        "system.methodHelp",
                        "add",
                        "pow",
                    ],
                )
                Assertion(Assertion.EQ)(
                    client["system.methodHelp"]("add"), "Adds two numbers together."
                )
                Assertion(Assertion.EQ)(client["add"](1, 2), 3)
                Assertion(Assertion.EQ)(client.pow(base=2), {"result": 4})
                Assertion(Assertion.EQ)(client.pow(base=2, exponent=3), {"result": 8})
        finally:
            server.stop()


if __name__ == "__main__":
    main()
