from fruition.database.engine import EngineFactory
from fruition.database.util import row_to_dict
from fruition.util.log import DebugUnifiedLoggingContext
from fruition.util.helpers import Assertion


def main() -> None:
    with DebugUnifiedLoggingContext():
        with EngineFactory() as factory:
            sqlite = factory.sqlite[":memory:"]
            version = row_to_dict(sqlite.execute("SELECT sqlite_version()"))
            Assertion(Assertion.EQ)(list(version.keys()), ["sqlite_version()"])


if __name__ == "__main__":
    main()
