from collections.abc import Callable

from requests import Response

ResponseSpec = Callable[[Response], None]


class ResponseSpecs:
    @staticmethod
    def status(expected: int) -> ResponseSpec:
        def confirm(response: Response) -> None:
            assert response.status_code == expected, (
                f"Expected HTTP {expected}, got {response.status_code}: {response.text}"
            )
        return confirm

    @staticmethod
    def request_ok() -> ResponseSpec:
        return ResponseSpecs.status(200)

    @staticmethod
    def request_created() -> ResponseSpec:
        return ResponseSpecs.status(201)

    @staticmethod
    def request_bad() -> ResponseSpec:
        return ResponseSpecs.status(400)
