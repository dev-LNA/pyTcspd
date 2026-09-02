# pyTcspd

Python client for interfacing with LNA's Telescope Control System controller's firmware.


Simple example, see [examples](examples/) for more.
```python
from lna_controller import Controller, SerialSender, TcsPdCommands

commands = TcsPdCommands()
controller = Controller(SerialSender(timeout_s=10), commands)
controller.open("/dev/ttyUSB0")
try:
    controller.send(commands.move_dome_to_tag(87))
    status = controller.send(commands.status_dome())
    print(status.tag, status.busy)
finally:
    controller.close()
```
