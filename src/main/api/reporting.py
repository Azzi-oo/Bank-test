"""JSON-вложения Allure без изменения отправляемых данных."""

import json
from collections.abc import Mapping

import allure


def redact(value):
    if isinstance(value, Mapping):
        return {
            key: "***" if any(part in str(key).lower() for part in
                              ("password", "token", "authorization", "cookie", "secret"))
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value


def attach_json(name: str, value) -> None:
    allure.attach(
        json.dumps(redact(value), ensure_ascii=False, indent=2, default=str),
        name=name, attachment_type=allure.attachment_type.JSON,
    )
