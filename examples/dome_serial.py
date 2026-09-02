"""Move the dome and read its status through a serial connection."""

from lna_controller import Controller, SerialSender, TcsPdCommands


def main() -> None:
    commands = TcsPdCommands()
    controller = Controller(
        sender=SerialSender(timeout_s=10),
        commands=commands,
    )

    controller.open("/dev/ttyUSB0")
    try:
        controller.send(commands.open_dome_slit())
        controller.send(commands.move_dome_to_tag(87))
        status = controller.send(commands.status_dome())
        print(f"tag={status.tag} busy={status.busy}")
        controller.send(commands.close_dome_slit())
    finally:
        controller.close()


if __name__ == "__main__":
    main()
