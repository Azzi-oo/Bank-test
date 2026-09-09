from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from requests import Session

from src.main.api.clients.base_client import BaseClient
from src.main.api.config import BASE_URL
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.specs.response_specs import ResponseSpec


RequestBody = BaseModel | dict[str, Any] | None


class HttpRequester:
    def __init__(
        self, request_spec: Mapping[str, str], endpoint: Endpoint,
        response_spec: ResponseSpec | None = None, *, base_url: str = BASE_URL,
        session: Session | None = None,
    ):
        self.request_spec = dict(request_spec)
        self.endpoint = endpoint
        self.response_spec = response_spec
        self.client = BaseClient(base_url, session=session)
