from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from requests import Response, Session

from src.main.api.fixtures.object_fixture import clean_user
from src.main.api.models.requests import CreateUserRequest, UserRole
from src.main.api.steps.admin_steps import AdminSteps


def test_cleanup_attempts_all_registered_users_after_failure():
    steps = Mock(spec=AdminSteps)
    steps.delete_user.side_effect = [RuntimeError('offline'), None]
    objects = [11, 12, 11]

    with pytest.raises(ExceptionGroup) as error:
        clean_user(objects, steps)

    assert [call.args[0] for call in steps.delete_user.call_args_list] == [12, 11]
    assert len(error.value.exceptions) == 1
    assert objects == []


def test_created_user_is_registered_even_if_response_schema_is_invalid():
    session = Mock(spec=Session)
    response = Response()
    response.status_code = 200
    response._content = b'{"id": 23, "username": "TestUser"}'
    session.request.return_value = response
    objects = []
    steps = AdminSteps(created_objects=objects, session=session)

    with pytest.raises(ValidationError):
        steps.create_user(CreateUserRequest(
            username='TestUser', password='Pas!sw0rd', role=UserRole.USER,
        ))

    assert objects == [23]


def test_cleanup_does_nothing_without_created_users():
    steps = Mock(spec=AdminSteps)
    clean_user([], steps)
    steps.delete_user.assert_not_called()


def test_unexpectedly_created_invalid_user_is_registered_before_failure():
    session = Mock(spec=Session)
    response = Response()
    response.status_code = 200
    response._content = b'{"id": 24}'
    session.request.return_value = response
    objects = []
    steps = AdminSteps(created_objects=objects, session=session)

    with pytest.raises(AssertionError, match='Expected HTTP 400, got 200'):
        steps.create_invalid_user({'username': 'ab'})

    assert objects == [24]
    assert session.request.call_args.kwargs['json'] == {'username': 'ab'}
