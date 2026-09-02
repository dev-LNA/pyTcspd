from __future__ import annotations

from lna_controller.tcp import TcpSender


class FakeSocket:
    def __init__(self):
        self.sent = b""
        self.closed = False
        self.response = bytearray(b"ACK 00\r")

    def settimeout(self, timeout: float) -> None:
        pass

    def sendall(self, data: bytes) -> None:
        self.sent += data

    def recv(self, size: int) -> bytes:
        if not self.response:
            return b""
        return bytes((self.response.pop(0),))

    def close(self) -> None:
        self.closed = True


def test_tcp_sender_uses_endpoint_and_cr_framing(monkeypatch) -> None:
    fake = FakeSocket()
    calls = []
    monkeypatch.setattr(
        "lna_controller.tcp.socket.create_connection",
        lambda address, timeout: calls.append((address, timeout)) or fake,
    )
    sender = TcpSender(timeout_s=3)
    sender.open("controller.example:4242")
    assert sender.send("MEADE PROG STATUS\r") == "ACK 00"
    assert calls == [(("controller.example", 4242), 3.0)]
    assert fake.sent == b"MEADE PROG STATUS\r"
    sender.close()
    assert fake.closed
