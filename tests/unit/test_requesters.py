from decimal import Decimal
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from requests import Response, Session

from src.main.api.clients.base_client import BaseClient
from src.main.api.config import REQUEST_TIMEOUT
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.requests import CreditRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.fixture
def session():
    return Mock(spec=Session)


def reply(status, body):
    response = Response()
    response.status_code = status
    response._content = body.encode()
    return response


def test_models_are_serialized_with_api_aliases(session):
    session.request.return_value = reply(201, '{}')
    requester = CrudRequester({}, Endpoint.CREDIT_REQUEST, session=session)

    requester.post(CreditRequest(account_id=7, amount=5000, term_months=12))

    assert session.request.call_args.kwargs['json'] == {
        'accountId': 7, 'amount': 5000, 'termMonths': 12,
    }


def test_invalid_payload_reaches_server_in_raw_mode(session):
    session.request.return_value = reply(400, '{"error":"invalid"}')
    body = {'username': 'ab', 'password': 'short', 'role': 'unknown'}
    requester = CrudRequester(
        {}, Endpoint.ADMIN_CREATE_USER, ResponseSpecs.request_bad(), session=session,
    )

    response = requester.post(body)

    assert response.status_code == 400
    assert session.request.call_args.kwargs['json'] == body


def test_status_is_checked_before_json_parsing(session):
    session.request.return_value = reply(502, '<html>Bad gateway</html>')
    requester = ValidateCrudRequester({}, Endpoint.ACCOUNT_CREATE, session=session)

    with pytest.raises(AssertionError, match='Expected HTTP 201, got 502'):
        requester.post()


def test_response_schema_is_validated(session):
    session.request.return_value = reply(201, '{"id": 1}')
    with pytest.raises(ValidationError, match='balance'):
        ValidateCrudRequester({}, Endpoint.ACCOUNT_CREATE, session=session).post()


def test_success_response_uses_decimal_and_no_body_for_account_creation(session):
    session.request.return_value = reply(201, '{"id": 1, "balance": 0.1}')

    account = ValidateCrudRequester({}, Endpoint.ACCOUNT_CREATE, session=session).post()

    assert account.balance == Decimal('0.1')
    assert 'json' not in session.request.call_args.kwargs


def test_custom_response_spec_runs_once(session):
    session.request.return_value = reply(201, '{"id": 1, "balance": 0}')
    check = Mock()

    ValidateCrudRequester({}, Endpoint.ACCOUNT_CREATE, check, session=session).post()

    check.assert_called_once_with(session.request.return_value)


def test_invalid_validated_request_does_not_send_http(session):
    with pytest.raises(ValidationError):
        ValidateCrudRequester({}, Endpoint.CREDIT_REQUEST, session=session).post({
            'accountId': 0, 'amount': -1, 'termMonths': 0,
        })
    session.request.assert_not_called()


def test_delete_formats_user_id_and_accepts_empty_response(session):
    session.request.return_value = reply(200, '')

    result = ValidateCrudRequester(
        {}, Endpoint.ADMIN_DELETE_USER, session=session, base_url='http://bank.test/',
    ).delete(user_id=42)

    assert result is None
    assert session.request.call_args.args == ('DELETE', 'http://bank.test/api/admin/users/42')
    assert 'json' not in session.request.call_args.kwargs


def test_missing_delete_id_never_calls_collection_endpoint(session):
    with pytest.raises(KeyError):
        CrudRequester({}, Endpoint.ADMIN_DELETE_USER, session=session).delete()
    session.request.assert_not_called()


def test_wrong_http_method_is_rejected_locally(session):
    with pytest.raises(ValueError, match='supports POST'):
        CrudRequester({}, Endpoint.ADMIN_CREATE_USER, session=session).delete(user_id=42)
    session.request.assert_not_called()


def test_tokens_do_not_leak_between_users_sharing_session(session):
    first = CrudRequester(RequestSpecs.auth_headers('first'), Endpoint.ACCOUNT_CREATE, session=session)
    second = CrudRequester(RequestSpecs.auth_headers('second'), Endpoint.ACCOUNT_CREATE, session=session)
    first.post()
    second.post()

    assert session.request.call_args_list[0].kwargs['headers']['Authorization'] == 'Bearer first'
    assert session.request.call_args_list[1].kwargs['headers']['Authorization'] == 'Bearer second'


def test_transport_accepts_header_and_timeout_overrides(session):
    client = BaseClient('http://bank.test/', 'original', session=session)

    client.get('/api/test', headers={'authorization': 'Bearer override'}, timeout=2)

    assert session.request.call_args.args == ('GET', 'http://bank.test/api/test')
    assert session.request.call_args.kwargs['timeout'] == 2
    assert session.request.call_args.kwargs['headers']['Authorization'] == 'Bearer override'
    assert client.headers['Authorization'] == 'Bearer original'
    client.get('/api/test')
    assert session.request.call_args.kwargs['timeout'] == REQUEST_TIMEOUT
