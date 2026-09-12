import json
from unittest.mock import patch

from requests import Response, Session
from unittest.mock import Mock

from src.main.api.clients.base_client import BaseClient
from src.main.api.reporting import attach_json


def test_http_attachments_mask_secrets_without_changing_request():
    session = Mock(spec=Session)
    response = Response()
    response.status_code = 200
    response._content = b'{"token":"private-token","user":{"id":7}}'
    session.request.return_value = response
    payload = {"username": "tester", "password": "private-password"}

    with patch("src.main.api.reporting.allure.attach") as attach:
        result = BaseClient("http://bank.test", session=session).post("/login", json=payload)

    assert result is response
    assert session.request.call_args.kwargs["json"]["password"] == "private-password"
    bodies = [json.loads(call.args[0]) for call in attach.call_args_list]
    assert bodies[0]["json"]["password"] == "***"
    assert bodies[1]["json"]["token"] == "***"
    assert bodies[1]["json"]["user"]["id"] == 7


def test_nested_secrets_are_masked_in_attachments():
    with patch("src.main.api.reporting.allure.attach") as attach:
        attach_json("Example", {"items": [{"accessToken": "secret", "amount": 10}]})
    assert json.loads(attach.call_args.args[0]) == {
        "items": [{"accessToken": "***", "amount": 10}],
    }
