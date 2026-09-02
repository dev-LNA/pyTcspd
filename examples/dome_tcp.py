"""Read the dome status through a TCP connection."""

from lna_controller import Controller, TcpSender, TcsPdCommands


def main() -> None:
    commands = TcsPdCommands()
    controller = Controller(
        sender=TcpSender(timeout_s=10),
        commands=commands,
    )

    controller.open("192.168.1.50:4000")
    try:
        status = controller.send(commands.status_dome())
        print(f"tag={status.tag} busy={status.busy}")
    finally:
        controller.close()


if __name__ == "__main__":
    main()
