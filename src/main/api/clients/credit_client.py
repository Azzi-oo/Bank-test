from src.main.api.clients.base_client import BaseClient


class CreditClient(BaseClient):
    def request_credit(
        self,
        account_id: int,
        amount: float,
        term_months: int,
    ):
        return self.post(
            "/api/credit/request",
            json={
                "accountId": account_id,
                "amount": amount,
                "termMonths": term_months,
            },
        )

    def get_history(self):
        return self.get("/api/credit/history")

    def repay_credit(
        self,
        credit_id: int,
        account_id: int,
        amount: float,
    ):
        return self.post(
            "/api/credit/repay",
            json={
                "creditId": credit_id,
                "accountId": account_id,
                "amount": amount,
            },
        )