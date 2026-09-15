from __future__ import annotations

from dataclasses import dataclass

from .interfaces import Command, CommandSet, Sender


@dataclass
class Controller[C: CommandSet, S: Sender]:
    sender: S
    commands: C

    def open(self, endpoint: str) -> None:
        self.sender.open(endpoint)

    def close(self) -> None:
        self.sender.close()

    def send[T](self, command: Command[T]) -> T:
        message, response_parser = command
        if not self.commands.is_valid_command(message):
            raise ValueError(f"Invalid command: {message!r}")
        response = self.sender.send(message)
        checked = self.commands.check_response(message, response)
        return response_parser(checked)
