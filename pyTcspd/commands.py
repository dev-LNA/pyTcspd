from __future__ import annotations

import re

from .interfaces import Command, Response
from .status import TcsPdStatus, TcsPdStatusParser


class CommandValidationError(ValueError):
    pass


class CommandResponseError(RuntimeError):
    def __init__(self, command: str, response: str):
        super().__init__(f"Controller rejected {command!r}: {response!r}")
        self.command = command
        self.response = response


class TcsPdCommands:
    _sexagesimal = re.compile(r"^-?\d{1,3} \d{2} \d{2}(?:\.\d+)?$")
    _flats = {"FLAT_WEAK", "FLAT_LO", "FLAT_HI", "FLAT_COUDE"}
    _command = re.compile(
        r"^(?:JIGA|AH|DEC|TUBO|CUP|ECASS|COUDE|MEADE) "
        r"(?:"
        r"PROG (?:STATUS|PARAR|RESET|ERROS|VERSAO|INPUTS|GRAVAR)"
        r"|UART1 (?:LINK|COM[12])"
        r"|DOMO MOVER = \d{3}"
        r"|TRAP (?:ABRIR|FECHAR|PARAR)"
        r"|(?:FLAT_WEAK|FLAT_LO|FLAT_HI|FLAT_COUDE) (?:LIGAR|DESLIGAR)"
        r"|EIXO (?:MOVER_ABS|MOVER_RAP|MOVER_REL|GUIAR_REL|SHIFT|GIRAR_VEL|MANETE|LIBERAR|SIDERAL)(?: = .+)?"
        r"|INVERSOR (?:DI|[PV]\d+)(?: = .+)?"
        r"|INDEXER (?:INICIALIZAR|LERHEXA|LERABS|ZERAR)"
        r")$"
    )

    @staticmethod
    def _response(message: str) -> Command[Response]:
        return message, Response

    @staticmethod
    def _validate_axis(axis: str, value: str | None = None) -> None:
        if axis not in {"AH", "DEC"}:
            raise CommandValidationError("Axis must be AH or DEC")
        if value is not None and not TcsPdCommands._sexagesimal.fullmatch(value):
            raise CommandValidationError("Positions must use '<degrees> MM SS.S'")

    def status_dome(self) -> Command[TcsPdStatus]:
        return ("MEADE PROG STATUS", TcsPdStatusParser("MEADE"))

    def status_cupola(self) -> Command[TcsPdStatus]:
        return ("CUP PROG STATUS", TcsPdStatusParser("CUP"))

    def status_ha(self) -> Command[TcsPdStatus]:
        return ("AH PROG STATUS", TcsPdStatusParser("AH"))

    def status_dec(self) -> Command[TcsPdStatus]:
        return ("DEC PROG STATUS", TcsPdStatusParser("DEC"))

    def stop(self) -> Command[Response]:
        return self._response("MEADE PROG PARAR")

    def reset(self) -> Command[Response]:
        return self._response("MEADE PROG RESET")

    def errors(self) -> Command[Response]:
        return self._response("MEADE PROG ERROS")

    def version(self) -> Command[Response]:
        return self._response("MEADE PROG VERSAO")

    def inputs(self) -> Command[Response]:
        return self._response("MEADE PROG INPUTS")

    def save(self) -> Command[Response]:
        return self._response("MEADE PROG GRAVAR")

    def link_uart(self) -> Command[Response]:
        return self._response("MEADE UART1 LINK")

    def select_uart(self, port: int) -> Command[Response]:
        if port not in (1, 2):
            raise CommandValidationError("UART port must be 1 or 2")
        return self._response(f"MEADE UART1 COM{port}")

    def move_dome_to_tag(self, tag: int) -> Command[Response]:
        if not 0 <= int(tag) <= 999:
            raise CommandValidationError("Dome tag must be between 0 and 999")
        return self._response(f"MEADE DOMO MOVER = {int(tag):03d}")

    def open_dome_slit(self) -> Command[Response]:
        return self._response("MEADE TRAP ABRIR")

    def close_dome_slit(self) -> Command[Response]:
        return self._response("MEADE TRAP FECHAR")

    def stop_dome_slit(self) -> Command[Response]:
        return self._response("MEADE TRAP PARAR")

    def turn_lamp_on(self, flat: str = "FLAT_WEAK") -> Command[Response]:
        if flat not in self._flats:
            raise CommandValidationError(f"Unsupported flat: {flat}")
        return self._response(f"MEADE {flat} LIGAR")

    def turn_lamp_off(self, flat: str = "FLAT_WEAK") -> Command[Response]:
        if flat not in self._flats:
            raise CommandValidationError(f"Unsupported flat: {flat}")
        return self._response(f"MEADE {flat} DESLIGAR")

    def move_ha_to(self, position: str, *, fast: bool = False) -> Command[Response]:
        self._validate_axis("AH", position)
        return self._response(f"AH EIXO {'MOVER_RAP' if fast else 'MOVER_ABS'} = {position}")

    def move_dec_to(self, position: str, *, fast: bool = False) -> Command[Response]:
        self._validate_axis("DEC", position)
        return self._response(f"DEC EIXO {'MOVER_RAP' if fast else 'MOVER_ABS'} = {position}")

    def move_ha_by(self, displacement: str) -> Command[Response]:
        self._validate_axis("AH", displacement)
        return self._response(f"AH EIXO MOVER_REL = {displacement}")

    def move_dec_by(self, displacement: str) -> Command[Response]:
        self._validate_axis("DEC", displacement)
        return self._response(f"DEC EIXO MOVER_REL = {displacement}")

    def guide_ha_by(self, correction: str) -> Command[Response]:
        self._validate_axis("AH", correction)
        return self._response(f"AH EIXO GUIAR_REL = {correction}")

    def guide_dec_by(self, correction: str) -> Command[Response]:
        self._validate_axis("DEC", correction)
        return self._response(f"DEC EIXO GUIAR_REL = {correction}")

    def shift_ha(self, centi_arcseconds: int) -> Command[Response]:
        if abs(int(centi_arcseconds)) > 1000:
            raise CommandValidationError("SHIFT is limited to +/-1000")
        return self._response(f"AH EIXO SHIFT = {int(centi_arcseconds)}")

    def shift_dec(self, centi_arcseconds: int) -> Command[Response]:
        if abs(int(centi_arcseconds)) > 1000:
            raise CommandValidationError("SHIFT is limited to +/-1000")
        return self._response(f"DEC EIXO SHIFT = {int(centi_arcseconds)}")

    def rotate_ha(self, milli_arcseconds: int) -> Command[Response]:
        return self._response(f"AH EIXO GIRAR_VEL = {int(milli_arcseconds)}")

    def rotate_dec(self, milli_arcseconds: int) -> Command[Response]:
        return self._response(f"DEC EIXO GIRAR_VEL = {int(milli_arcseconds)}")

    def read_ha_hand_controller(self) -> Command[Response]:
        return self._response("AH EIXO MANETE")

    def read_dec_hand_controller(self) -> Command[Response]:
        return self._response("DEC EIXO MANETE")

    def release_ha_limit(self) -> Command[Response]:
        return self._response("AH EIXO LIBERAR")

    def release_dec_limit(self) -> Command[Response]:
        return self._response("DEC EIXO LIBERAR")

    def set_ha_sidereal_tracking(self, enabled: bool) -> Command[Response]:
        return self._response(f"AH EIXO SIDERAL = {'LIGAR' if enabled else 'DESLIGAR'}")

    def set_dec_sidereal_tracking(self, enabled: bool) -> Command[Response]:
        return self._response(f"DEC EIXO SIDERAL = {'LIGAR' if enabled else 'DESLIGAR'}")

    def set_inverter_inputs(self, bits: str) -> Command[Response]:
        if any(bit not in "01X " for bit in bits):
            raise CommandValidationError("DI accepts only 0, 1, X and spaces")
        return self._response(f"MEADE INVERSOR DI = {bits}")

    def access_inverter_register(
        self, register: str, value: object | None = None
    ) -> Command[Response]:
        if not re.fullmatch(r"[PV]\d+", register):
            raise CommandValidationError("Register must look like Pnnn or Vnn")
        suffix = "" if value is None else f" = {value}"
        return self._response(f"MEADE INVERSOR {register}{suffix}")

    def initialize_indexer(self) -> Command[Response]:
        return self._response("MEADE INDEXER INICIALIZAR")

    def read_indexer_hex_position(self) -> Command[Response]:
        return self._response("MEADE INDEXER LERHEXA")

    def read_indexer_absolute_position(self) -> Command[Response]:
        return self._response("MEADE INDEXER LERABS")

    def zero_indexer_position(self) -> Command[Response]:
        return self._response("MEADE INDEXER ZERAR")

    def is_valid_command(self, command: str) -> bool:
        return bool(self._command.fullmatch(command.strip()))

    def check_response(self, command: str, response: str) -> str:
        if not response.strip() or response.strip().upper().startswith("NAK"):
            raise CommandResponseError(command, response)
        return response
