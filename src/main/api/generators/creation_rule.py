import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CreationRule:
    """Задаёт регулярное выражение для генерации значения поля модели."""

    regex: str

    def __post_init__(self) -> None:
        re.compile(self.regex)
