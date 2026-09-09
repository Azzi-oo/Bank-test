import random
import re
from enum import Enum
from typing import Any, TypeVar
from uuid import uuid4

import rstr
from pydantic import BaseModel

from src.main.api.generators.creation_rule import CreationRule

ModelT = TypeVar("ModelT", bound=BaseModel)


class RandomModelGenerator:
    """Создаёт Pydantic-модели по правилам полей с проверкой итоговых данных."""

    @staticmethod
    def generate(model_type: type[ModelT], **overrides: Any) -> ModelT:
        """Генерирует обязательные поля, сохраняя значения по умолчанию и явные переопределения."""
        unknown = overrides.keys() - model_type.model_fields.keys()
        if unknown:
            raise ValueError(f"Unknown fields for {model_type.__name__}: {', '.join(sorted(unknown))}")
        data = dict(overrides)
        for name, field in model_type.model_fields.items():
            if name in data or not field.is_required():
                continue
            rules = [item for item in field.metadata if isinstance(item, CreationRule)]
            if len(rules) > 1:
                raise ValueError(f"Multiple CreationRule definitions for {name}")
            if rules:
                value = rstr.xeger(rules[0].regex)
                if re.fullmatch(rules[0].regex, value) is None:
                    raise ValueError(f"Generated value does not match CreationRule for {name}")
                data[name] = value
            else:
                data[name] = RandomModelGenerator._generate_value(field.annotation)
        return model_type.model_validate(data, by_name=True)

    @staticmethod
    def _generate_value(field_type: Any) -> Any:
        """Генерирует простые значения; для остальных типов требуется явное переопределение."""
        if field_type is str:
            return uuid4().hex
        if field_type is bool:
            return random.choice((True, False))
        if field_type is int:
            return random.randint(1, 100)
        if field_type is float:
            return random.uniform(1, 100)
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            return random.choice(list(field_type))
        raise TypeError(f"Unsupported field type {field_type!r}; provide an explicit value")
