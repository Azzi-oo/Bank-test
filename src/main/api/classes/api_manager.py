import requests

from src.main.api.config import BASE_URL
from src.main.api.steps.admin_steps import AdminSteps
from src.main.api.steps.user_steps import UserSteps


class ApiManager:
    """Own a session for one test and keep authentication local to each steps object."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_objects: list[int] = []
        self.user_steps = UserSteps(base_url=base_url, session=self.session)
        self._admin_steps: AdminSteps | None = None

    @property
    def admin_steps(self) -> AdminSteps:
        if self._admin_steps is None:
            raise RuntimeError("Call login_admin before accessing admin_steps")
        return self._admin_steps

    def login_admin(self, username: str, password: str) -> None:
        login = self.user_steps.login(username, password)
        self._admin_steps = AdminSteps(
            base_url=self.base_url, token=login.token, session=self.session,
            created_objects=self.created_objects,
        )

    def login_user(self, username: str, password: str) -> UserSteps:
        login = self.user_steps.login(username, password)
        return UserSteps(base_url=self.base_url, token=login.token, session=self.session)

    def close(self) -> None:
        self.session.close()
