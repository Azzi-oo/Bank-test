

from main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from main.api.models.requests import CreateUserRequest
from main.api.specs.request_specs import RequestSpecs
from main.api.specs.response_specs import ResponseSpecs
from main.api.tests.conftest import username


class AdminSteps(BaseSteps):
    def create_user(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            endpoint=create_user_request.endpoint,
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)