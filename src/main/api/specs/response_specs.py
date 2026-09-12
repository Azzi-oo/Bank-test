from collections.abc import Callable

import allure
from requests import Response

ResponseSpec = Callable[[Response], None]


class ResponseSpecs:
    @staticmethod
    def status(expected: int) -> ResponseSpec:
        def confirm(response: Response) -> None:
            with allure.step(f"Проверить HTTP-статус: {expected}"):
                assert response.status_code == expected, (
                    f"Expected HTTP {expected}, got {response.status_code}"
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
