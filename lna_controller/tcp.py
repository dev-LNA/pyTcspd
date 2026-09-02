from __future__ import annotations

import socket
import time
from logging import Logger


class TcpSender:
    def __init__(self, *, timeout_s: float = 10.0, logger: Logger | None = None):
        self._timeout = float(timeout_s)
        self._logger = logger
        self._socket: socket.socket | None = None

    def open(self, endpoint: str) -> None:
        host, separator, port_text = endpoint.rpartition(":")
        if not separator or not host or not port_text.isdigit():
            raise ValueError("TCP endpoint must use 'host:port' syntax")
        self._socket = socket.create_connection(
            (host, int(port_text)), timeout=self._timeout
        )
        self._socket.settimeout(self._timeout)

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
        self._socket = None

    def is_open(self) -> bool:
        return self._socket is not None

    def send(self, message: str) -> str:
        if self._socket is None:
            raise RuntimeError("TCP connection is not open")
        wire_message = f"{message.rstrip(chr(13))}\r".encode()
        if self._logger:
            self._logger.debug("[tcp write] %r", message)
        self._socket.sendall(wire_message)
        response = bytearray()
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            try:
                chunk = self._socket.recv(1)
            except TimeoutError:
                break
            if not chunk:
                break
            response.extend(chunk)
            if chunk == b"\r":
                break
        decoded = response.decode(errors="replace").replace("\r", "")
        if self._logger:
            self._logger.debug("[tcp read ] %r", decoded)
        return decoded
