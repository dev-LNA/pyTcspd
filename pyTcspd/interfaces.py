from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, TypeAlias, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class Response:
    raw: str


ResponseParser = Callable[[str], T]
Command: TypeAlias = tuple[str, ResponseParser[T]]


class Sender(Protocol):
    def open(self, endpoint: str) -> None: ...

    def close(self) -> None: ...

    def send(self, message: str) -> str: ...

    def is_open(self) -> bool: ...


class CommandSet(Protocol):
    def is_valid_command(self, command: str) -> bool: ...

    def check_response(self, command: str, response: str) -> str: ...
