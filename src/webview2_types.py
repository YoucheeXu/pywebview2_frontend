from typing import TypedDict, NotRequired

class ServerConfig(TypedDict):
    serverUrl: str
    apiPrefix: str
    timeout: int
    enableMock: bool
    app: NotRequired["str"]
