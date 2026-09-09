from unittest.mock import Mock

from requests import Response, Session

from src.main.api.models.requests import CreateUserRequest, UserRole
from src.main.api.steps.user_steps import UserSteps


def reply(status, body):
    response = Response()
    response.status_code = status
    response._content = body.encode()
    return response


def test_create_account_with_credentials_keeps_existing_authentication():
    session = Mock(spec=Session)
    session.request.side_effect = [
        reply(200, '{"token":"new-token","user":{"username":"NewUser","role":"ROLE_USER"}}'),
        reply(201, '{"id":7,"balance":0}'),
        reply(201, '{"id":8,"balance":0}'),
    ]
    steps = UserSteps(base_url='http://bank.test/', token='original-token', session=session)
    request = CreateUserRequest(username='NewUser', password='Pas!sw0rd', role=UserRole.USER)

    assert steps.create_account(request).id == 7
    assert steps.create_account().id == 8

    login, new_account, original_account = session.request.call_args_list
    assert login.args == ('POST', 'http://bank.test/api/auth/token/login')
    assert 'Authorization' not in login.kwargs['headers']
    assert login.kwargs['json'] == {'username': 'NewUser', 'password': 'Pas!sw0rd'}
    assert new_account.args == ('POST', 'http://bank.test/api/account/create')
    assert new_account.kwargs['headers']['Authorization'] == 'Bearer new-token'
    assert 'json' not in new_account.kwargs
    assert original_account.kwargs['headers']['Authorization'] == 'Bearer original-token'
    assert steps.token == 'original-token'
