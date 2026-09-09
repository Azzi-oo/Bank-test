from typing import Callable, Dict
from main.api.foundation.endpoint import Endpoint


class HttpRequester:
    def __init__(self) -> None:
        def __init__(self, requst_spec: Dict[str, str], endpoint: Endpoint, response_spec: Callable):
            self.request_spec = requst_spec
            self.endpoint = endpoint
            self.response_spec = response_spec