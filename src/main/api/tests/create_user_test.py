import requests
import pytest

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateUser:
    def test_create_user_valid(self, username):
        login_user_request = LoginUserRequest(username="admin", password="123456")
        
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json=login_user_request.model_dump(),
            headers={
                'Content-Type': 'application/json',
                "Accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        token = login_admin_response.json().get("token")

        create_user_request = CreateUserRequest(username="Maxx224", password="Pas!sw0rd", role="ROLE_USER")
        
    
        response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json=create_user_request.model_dump(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 200
        create_user_response = CreateUserResponse(**response.json())
        assert create_user_request.username == create_user_response.user.username
        assert create_user_request.role == create_user_response.user.role

    
    @pytest.mark.parametrize(
        "username, password", 
        [
            ("абв", "Pas!sw0rd"),
            ("аб", "Pas!sw0rd"),
            ("abv!", "Pas!sw0rd"),
            ("Maxx1", "Pas!sw0rdд"),
            ("Maxx2", "Pas!sw0"),
            ("Maxx3", "pas!sw0rd"),
            ("Maxx4", "PASSWORD"),
            ("Maxx5", "PAS!SW0RD"),
            ("Maxx6", "PAS!SWRRD"),
        ]
    )
    def test_create_user_with_invalid(self, username, password):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'Content-Type': 'application/json',
                "Accept": "application/json"
            }
        )
        
        assert login_admin_response.status_code == 200
        token = login_admin_response.json().get("token")
        
        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": password,
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        assert create_user_response.status_code == 400
