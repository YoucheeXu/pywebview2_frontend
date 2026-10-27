from typing import NotRequired, TypedDict


class ServerConfig(TypedDict):
    serverUrl: str
    apiPrefix: str
    timeout: int
    enableMock: bool
    app: NotRequired["str"]
