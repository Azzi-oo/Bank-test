from requests import Session

from src.main.api.config import BASE_URL
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpec


class BaseSteps:
    def __init__(
        self, *, base_url: str = BASE_URL, token: str | None = None,
        session: Session | None = None,
    ):
        self.base_url = base_url
        self.token = token
        self.session = session

    @property
    def request_spec(self) -> dict[str, str]:
        return (RequestSpecs.auth_headers(self.token) if self.token
                else RequestSpecs.base_headers())

    def raw(self, endpoint: Endpoint, response_spec: ResponseSpec | None = None) -> CrudRequester:
        return CrudRequester(
            self.request_spec, endpoint, response_spec,
            base_url=self.base_url, session=self.session,
        )

    def validated(self, endpoint: Endpoint) -> ValidateCrudRequester:
        return ValidateCrudRequester(
            self.request_spec, endpoint, base_url=self.base_url, session=self.session,
        )
