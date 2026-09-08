from src.main.api.clients.base_client import BaseClient


class AccountClient(BaseClient):
    def create_account(self):
        return self.post("/api/account/create")

    def deposit(self, account_id: int, amount: float):
        return self.post(
            "/api/account/deposit",
            json={
                "accountId": account_id,
                "amount": amount,
            },
        )

    def transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: float,
    ):
        return self.post(
            "/api/account/transfer",
            json={
                "fromAccountId": from_account_id,
                "toAccountId": to_account_id,
                "amount": amount,
            },
        )

    def get_transactions(self, account_id: int):
        return self.get(f"/api/account/transactions/{account_id}")