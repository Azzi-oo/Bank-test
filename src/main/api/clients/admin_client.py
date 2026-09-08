from src.main.api.clients.base_client import BaseClient


class AdminClient(BaseClient):
    def create_user(self, username: str, password: str, role: str):
        return self.post(
            "/api/admin/create",
            json={
                "username": username,
                "password": password,
                "role": role,
            },
        )