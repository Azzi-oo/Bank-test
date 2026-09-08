from src.main.api.clients.base_client import BaseClient


class AuthClient(BaseClient):
    def login(self, username: str, password: str):
        return self.post(
            "/api/auth/token/login",
            json={
                "username": username,
                "password": password,
            },
        )