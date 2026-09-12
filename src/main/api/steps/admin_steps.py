import allure

from typing import Any

from requests import Response

from src.main.api.models.auth import LoginResponse
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import CreateUserRequest, LoginRequest
from src.main.api.models.user import CreateUserResponse
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps
from src.main.api.steps.user_steps import UserSteps


class AdminSteps(BaseSteps):
    def __init__(self, *, created_objects: list[int], **kwargs):
        super().__init__(**kwargs)
        self.created_objects = created_objects

    def create_user(self, create_user_request: CreateUserRequest) -> CreateUserResponse:
        with allure.step('Создать пользователя'):
            response = self.raw(Endpoint.ADMIN_CREATE_USER, ResponseSpecs.request_ok()).post(
                create_user_request,
            )
            data = response.json()
            user_id = data.get("id")
            if type(user_id) is int and user_id > 0:
                self.created_objects.append(user_id)
            return CreateUserResponse.model_validate(data)

    def delete_user(self, user_id: int) -> None:
        with allure.step('Удалить тестового пользователя'):
            if user_id <= 0:
                raise ValueError("user_id must be positive")
            response = self.raw(Endpoint.ADMIN_DELETE_USER).delete(user_id=user_id)
            if response.status_code != 404:
                ResponseSpecs.status(Endpoint.ADMIN_DELETE_USER.value.success_status)(response)

    def create_invalid_user(self, create_user_request: CreateUserRequest | dict[str, Any]) -> Response:
        """Проверяет отказ в создании пользователя и учитывает его для очистки при неожиданном успехе."""
        with allure.step('Проверить отказ в создании пользователя'):
            response = self.raw(Endpoint.ADMIN_CREATE_USER).post(create_user_request)
            if response.status_code == 200:
                user_id = response.json().get("id")
                if type(user_id) is int and user_id > 0:
                    self.created_objects.append(user_id)
            ResponseSpecs.request_bad()(response)
            return response

    def login_user(self, login_user_request: LoginRequest) -> LoginResponse:
        """Выполняет вход по логину и паролю без передачи токена администратора."""
        with allure.step('Войти созданным пользователем'):
            return UserSteps(base_url=self.base_url, session=self.session).login(
                login_user_request.username, login_user_request.password,
            )
