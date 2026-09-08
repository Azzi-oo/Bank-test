import pytest
import requests


BASE_URL = "http://localhost:4111"


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay(self, username):
        admin_login = requests.post(
            f"{BASE_URL}/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456",
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_token = admin_login.json()["token"]

        create_user = requests.post(
            f"{BASE_URL}/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET",
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {admin_token}",
            },
        )
        assert create_user.status_code == 200, create_user.text

        user_login = requests.post(
            f"{BASE_URL}/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd",
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        assert user_login.status_code == 200, user_login.text

        user_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {user_login.json()['token']}",
        }

        create_account = requests.post(
            f"{BASE_URL}/api/account/create",
            headers=user_headers,
        )
        assert create_account.status_code == 201, create_account.text
        account_id = create_account.json()["id"]

        credit_request = requests.post(
            f"{BASE_URL}/api/credit/request",
            json={
                "accountId": account_id,
                "amount": 5000,
                "termMonths": 12,
            },
            headers=user_headers,
        )
        assert credit_request.status_code == 201, credit_request.text

        credit_history = requests.get(
            f"{BASE_URL}/api/credit/history",
            headers=user_headers,
        )
        assert credit_history.status_code == 200, credit_history.text

        history_data = credit_history.json()

        if isinstance(history_data, list):
            credits = history_data
        else:
            credits = history_data.get("credits", history_data.get("data", []))

        assert credits, f"Кредит не появился в истории: {credit_history.text}"

        user_credit = next(
            (
                credit
                for credit in credits
                if credit.get("accountId") == account_id
            ),
            None,
        )

        assert user_credit is not None, (
            f"Кредит для счёта {account_id} не найден: {credit_history.text}"
        )

        credit_id = user_credit["creditId"]

        credit_repay = requests.post(
            f"{BASE_URL}/api/credit/repay",
            json={
                "creditId": credit_id,
                "accountId": account_id,
                "amount": 5000,
            },
            headers=user_headers,
        )
        assert credit_repay.status_code == 200, credit_repay.text
