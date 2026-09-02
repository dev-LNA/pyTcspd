"""Move both telescope axes and read an axis status."""

from lna_controller import Controller, SerialSender, TcsPdCommands


def main() -> None:
    commands = TcsPdCommands()
    controller = Controller(
        sender=SerialSender(timeout_s=10),
        commands=commands,
    )

    controller.open("/dev/ttyUSB0")
    try:
        controller.send(commands.move_ah_to("10 30 45.6"))
        controller.send(commands.move_dec_to("20 00 00.0", fast=True))
        controller.send(commands.set_ah_sidereal_tracking(True))

        status = controller.send(commands.status_ah())
        print(f"position={status.value} tracking={status.fields['tracking']}")

        controller.send(commands.stop())
    finally:
        controller.close()


if __name__ == "__main__":
    main()
