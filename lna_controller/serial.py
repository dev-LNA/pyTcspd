from __future__ import annotations

import time
from logging import Logger

import serial


class SerialSender:
    def __init__(
        self,
        *,
        baudrate: int = 9600,
        timeout_s: float = 10.0,
        logger: Logger | None = None,
    ):
        self._baudrate = baudrate
        self._timeout = float(timeout_s)
        self._logger = logger
        self._port: serial.Serial | None = None

    def open(self, endpoint: str) -> None:
        self._port = serial.Serial(
            endpoint, baudrate=self._baudrate, timeout=self._timeout
        )

    def close(self) -> None:
        if self._port is not None and self._port.is_open:
            self._port.close()
        self._port = None

    def is_open(self) -> bool:
        return self._port is not None and self._port.is_open

    def send(self, message: str) -> str:
        if self._port is None or not self._port.is_open:
            raise RuntimeError("Serial port is not open")
        self._port.reset_output_buffer()
        self._port.reset_input_buffer()
        wire_message = f"{message.rstrip(chr(13))}\r".encode()
        if self._logger:
            self._logger.debug("[serial write] %r", message)
        if self._port.write(wire_message) != len(wire_message):
            raise RuntimeError("Serial write failed")
        response = bytearray()
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            chunk = self._port.read(1)
            if chunk:
                response.extend(chunk)
                if chunk == b"\r":
                    break
        else:
            self._port.reset_input_buffer()
            self._port.reset_output_buffer()
        decoded = response.decode(errors="replace").replace("\r", "")
        if self._logger:
            self._logger.debug("[serial read ] %r", decoded)
        return decoded
