from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import CreateUserRequest
from src.main.api.models.user import CreateUserResponse
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):
    def __init__(self, *, created_objects: list[int], **kwargs):
        super().__init__(**kwargs)
        self.created_objects = created_objects

    def create_user(self, create_user_request: CreateUserRequest) -> CreateUserResponse:
        response = self.raw(Endpoint.ADMIN_CREATE_USER, ResponseSpecs.request_ok()).post(
            create_user_request,
        )
        data = response.json()
        # Register the resource before schema validation so teardown survives its failure.
        user_id = data.get("id")
        if type(user_id) is int and user_id > 0:
            self.created_objects.append(user_id)
        return CreateUserResponse.model_validate(data)

    def delete_user(self, user_id: int) -> None:
        if user_id <= 0:
            raise ValueError("user_id must be positive")
        response = self.raw(Endpoint.ADMIN_DELETE_USER).delete(user_id=user_id)
        # Already deleted is safe during teardown; other failures must remain visible.
        if response.status_code != 404:
            ResponseSpecs.status(Endpoint.ADMIN_DELETE_USER.value.success_status)(response)
