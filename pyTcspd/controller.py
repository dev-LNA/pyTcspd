from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from .interfaces import Command, CommandSet, Sender

T = TypeVar("T")


@dataclass
class Controller:
    sender: Sender
    commands: CommandSet

    def open(self, endpoint: str) -> None:
        self.sender.open(endpoint)

    def close(self) -> None:
        self.sender.close()

    def send(self, command: Command[T]) -> T:
        message, response_parser = command
        if not self.commands.is_valid_command(message):
            raise ValueError(f"Invalid command: {message!r}")
        response = self.sender.send(message)
        checked = self.commands.check_response(message, response)
        return response_parser(checked)
