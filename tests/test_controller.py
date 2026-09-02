from __future__ import annotations

import pytest

from lna_controller import Command, Controller, TcsPdCommands, TcsPdStatus, TcsPdStatusParser
from lna_controller.interfaces import Response
from lna_controller.commands import (
    CommandResponseError,
    CommandValidationError,
)


class FakeSender:
    def __init__(self, response: str = "ACK 00"):
        self.response = response
        self.messages: list[str] = []
        self.opened = False

    def open(self, endpoint: str) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def is_open(self) -> bool:
        return self.opened

    def send(self, message: str) -> str:
        self.messages.append(message)
        return self.response


def test_default_commands_cover_dome_and_protocol_parameters() -> None:
    commands = TcsPdCommands()
    assert commands.move_dome_to_tag(7)[0] == "MEADE DOMO MOVER = 007"
    assert commands.move_dec_to("01 23 45.6")[0] == (
        "DEC EIXO MOVER_ABS = 01 23 45.6"
    )
    assert commands.move_ah_by("00 05 20.4")[0] == "AH EIXO MOVER_REL = 00 05 20.4"
    assert commands.guide_dec_by("00 00 01.0")[0] == "DEC EIXO GUIAR_REL = 00 00 01.0"
    assert commands.shift_ah(10)[0] == "AH EIXO SHIFT = 10"
    assert commands.rotate_dec(20)[0] == "DEC EIXO GIRAR_VEL = 20"
    assert commands.set_ah_sidereal_tracking(True)[0] == "AH EIXO SIDERAL = LIGAR"
    assert commands.set_dec_sidereal_tracking(False)[0] == "DEC EIXO SIDERAL = DESLIGAR"
    assert commands.stop_dome_slit()[0] == "MEADE TRAP PARAR"
    assert commands.select_uart(2)[0] == "MEADE UART1 COM2"


def test_custom_command_set_is_injected() -> None:
    class CustomCommands:
        def command(self, parameter: int) -> str:
            if parameter < 0:
                raise ValueError("parameter must be non-negative")
            return f"CUSTOM MOVE = {parameter}"

        def is_valid_command(self, command: str) -> bool:
            return command.startswith("CUSTOM MOVE = ")

        def check_response(self, command: str, response: str) -> str:
            if response != "ACK 00":
                raise RuntimeError(response)
            return response

    sender = FakeSender()
    commands = CustomCommands()
    controller = Controller(
        sender,
        commands=commands,
    )
    assert controller.send((commands.command(12), Response)) == Response("ACK 00")
    assert sender.messages == ["CUSTOM MOVE = 12"]


def test_command_function_validates_arguments_before_transport() -> None:
    sender = FakeSender()
    commands = TcsPdCommands()
    controller = Controller(
        sender,
        commands=commands,
    )
    with pytest.raises(CommandValidationError):
        commands.move_dome_to_tag(1000)
    assert sender.messages == []


def test_invalid_complete_command_is_rejected_before_transport() -> None:
    sender = FakeSender()
    controller = Controller(
        sender,
        commands=TcsPdCommands(),
    )
    with pytest.raises(ValueError, match="Invalid command"):
        controller.send(("MEADE UNKNOWN COMMAND", Response))
    assert sender.messages == []


def test_status_parses_dome_tag_and_flags() -> None:
    status = TcsPdStatusParser()("        087     1")
    assert status.tag == 87
    assert status.address == "MEADE"
    assert status.busy is True
    assert status.initialized is True
    assert status.raw == "        087     1"


def test_send_can_return_a_typed_parsed_response() -> None:
    controller = Controller(
        FakeSender("        087     1"),
        commands=TcsPdCommands(),
    )
    status = controller.send(TcsPdCommands().status_dome())
    assert status.tag == 87


def test_status_command_addresses_are_explicit() -> None:
    commands = TcsPdCommands()
    assert commands.status_dome()[0] == "MEADE PROG STATUS"
    assert commands.status_cupola()[0] == "CUP PROG STATUS"
    assert commands.status_ah()[0] == "AH PROG STATUS"
    assert commands.status_dec()[0] == "DEC PROG STATUS"


def test_status_command_is_typed_as_status_command() -> None:
    command: Command[TcsPdStatus] = TcsPdCommands().status_dome()
    assert command[0] == "MEADE PROG STATUS"


def test_send_raises_for_nak() -> None:
    sender = FakeSender("NAK 00")
    controller = Controller(
        sender,
        commands=TcsPdCommands(),
    )
    with pytest.raises(CommandResponseError):
        controller.send(TcsPdCommands().stop())
