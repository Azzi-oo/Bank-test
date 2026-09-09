from pydantic import BaseModel
from requests import Response

from src.main.api.foundation.http_requester import HttpRequester, RequestBody


class CrudRequester(HttpRequester):
    """Send raw payloads as well as models, including invalid data for negative tests."""

    def _send(self, method: str, model: RequestBody = None, **path_params: int) -> Response:
        config = self.endpoint.value
        if method != config.method:
            raise ValueError(f"{self.endpoint.name} supports {config.method}, not {method}")
        path = config.url.format(**path_params)
        kwargs = {}
        if model is not None:
            kwargs["json"] = (
                model.model_dump(mode="json", by_alias=True)
                if isinstance(model, BaseModel) else model
            )
        response = self.client.request(method, path, headers=self.request_spec, **kwargs)
        if self.response_spec is not None:
            self.response_spec(response)
        return response

    def post(self, model: RequestBody = None, **path_params: int) -> Response:
        return self._send("POST", model, **path_params)

    def get(self, **path_params: int) -> Response:
        return self._send("GET", **path_params)

    def delete(self, **path_params: int) -> Response:
        return self._send("DELETE", **path_params)
