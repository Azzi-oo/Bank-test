import requests
from requests.structures import CaseInsensitiveDict

from src.main.api.config import REQUEST_TIMEOUT
from src.main.api.specs.request_specs import RequestSpecs


class BaseClient:
    def __init__(
        self, base_url: str, token: str | None = None,
        *, session: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = session

    @property
    def headers(self) -> dict[str, str]:
        if self.token:
            return RequestSpecs.auth_headers(self.token)
        return RequestSpecs.base_headers()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        headers = CaseInsensitiveDict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        send = self.session.request if self.session is not None else requests.request
        return send(
            method, f"{self.base_url}/{path.lstrip('/')}", headers=headers, **kwargs,
        )

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
