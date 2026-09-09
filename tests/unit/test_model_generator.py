import re
from typing import Annotated

import pytest
from pydantic import BaseModel, Field, ValidationError

from src.main.api.generators.creation_rule import CreationRule
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.requests import CreateUserRequest, UserRole
from src.main.api.models.user import CreateUserRequest as ExportedCreateUserRequest


def test_generated_users_follow_rules_and_use_the_shared_request_model():
    assert ExportedCreateUserRequest is CreateUserRequest
    for _ in range(25):
        user = RandomModelGenerator.generate(CreateUserRequest)
        assert re.fullmatch(r'[A-Za-z0-9]{15}', user.username)
        assert re.fullmatch(r'[A-Z]{3}[a-z][0-9]{2}[!$_]{4}', user.password)
        assert user.role is UserRole.USER


def test_explicit_values_override_generation_rules():
    user = RandomModelGenerator.generate(
        CreateUserRequest, username='CustomUser', role=UserRole.CREDIT_SECRET,
    )
    assert user.username == 'CustomUser'
    assert user.role is UserRole.CREDIT_SECRET


def test_invalid_override_is_validated():
    with pytest.raises(ValidationError):
        RandomModelGenerator.generate(CreateUserRequest, username='ab')


def test_unknown_override_is_rejected():
    with pytest.raises(ValueError, match='usernmae'):
        RandomModelGenerator.generate(CreateUserRequest, usernmae='CustomUser')


class GeneratedValues(BaseModel):
    number: Annotated[int, CreationRule(regex=r'^[1-9][0-9]$')] = Field(alias='numberValue')
    enabled: bool
    label: str = 'default'
    items: list[int] = Field(default_factory=list)


def test_numeric_rules_aliases_defaults_and_factories():
    first = RandomModelGenerator.generate(GeneratedValues)
    second = RandomModelGenerator.generate(GeneratedValues)
    assert 10 <= first.number <= 99
    assert isinstance(first.enabled, bool)
    assert first.label == 'default'
    first.items.append(1)
    assert second.items == []


class UnsupportedValues(BaseModel):
    items: list[int]


def test_unsupported_type_requires_an_explicit_value():
    with pytest.raises(TypeError, match='explicit value'):
        RandomModelGenerator.generate(UnsupportedValues)
    assert RandomModelGenerator.generate(UnsupportedValues, items=[1]).items == [1]


def test_invalid_regex_is_rejected_when_rule_is_defined():
    with pytest.raises(re.error):
        CreationRule(regex='[')


def test_generation_rules_do_not_block_negative_request_data():
    request = CreateUserRequest(username='абв', password='short', role=UserRole.USER)
    assert request.username == 'абв'
