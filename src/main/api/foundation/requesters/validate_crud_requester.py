from pydantic import BaseModel

from src.main.api.foundation.http_requester import RequestBody

from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.specs.response_specs import ResponseSpecs


class ValidateCrudRequester:
    """Validate status before deserializing the success response schema."""

    def __init__(self, request_spec, endpoint, response_spec=None, **kwargs):
        self.endpoint = endpoint
        self.crud_requester = CrudRequester(
            request_spec, endpoint,
            response_spec if response_spec is not None
            else ResponseSpecs.status(endpoint.value.success_status),
            **kwargs,
        )

    def _parse(self, response) -> BaseModel | None:
        response_model = self.endpoint.value.response_model
        if response_model is None:
            return None
        return response_model.model_validate(response.json())

    def post(self, model: RequestBody = None, **path_params: int) -> BaseModel | None:
        request_model = self.endpoint.value.request_model
        if request_model is not None:
            model = request_model.model_validate(model)
        elif model is not None:
            raise ValueError(f"{self.endpoint.name} does not accept a request body")
        return self._parse(self.crud_requester.post(model, **path_params))

    def get(self, **path_params: int) -> BaseModel | None:
        return self._parse(self.crud_requester.get(**path_params))

    def delete(self, **path_params: int) -> BaseModel | None:
        return self._parse(self.crud_requester.delete(**path_params))
