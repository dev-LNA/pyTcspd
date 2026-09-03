"""Use the controller without hardware for a simple local smoke test."""

from pyTcspd import Controller, TcsPdCommands


class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def open(self, endpoint: str) -> None:
        pass

    def close(self) -> None:
        pass

    def is_open(self) -> bool:
        return True

    def send(self, message: str) -> str:
        self.messages.append(message)
        if message.endswith("PROG STATUS"):
            return "        087     1"
        return "ACK 00"


def main() -> None:
    commands = TcsPdCommands()
    controller = Controller(FakeSender(), commands)

    status = controller.send(commands.status_dome())
    controller.send(commands.move_dome_to_tag(87))

    print(f"tag={status.tag} messages={controller.sender.messages}")


if __name__ == "__main__":
    main()
