class RequestSpecs:
    @staticmethod
    def base_headers() -> dict[str, str]:
        return {"Content-Type": "application/json", "Accept": "application/json"}

    @staticmethod
    def auth_headers(token: str) -> dict[str, str]:
        return {**RequestSpecs.base_headers(), "Authorization": f"Bearer {token}"}

    @staticmethod
    def unauth_headers() -> dict[str, str]:
        return RequestSpecs.base_headers()
