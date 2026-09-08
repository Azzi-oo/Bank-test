import requests


class BaseClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url
        self.token = token

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def get(self, path: str, **kwargs):
        return requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            timeout=10,
            **kwargs,
        )

    def post(self, path: str, **kwargs):
        return requests.post(
            f"{self.base_url}{path}",
            headers=self.headers,
            timeout=10,
            **kwargs,
        )