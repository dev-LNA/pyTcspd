# Examples

Run the examples from the project root with the project environment active:

```bash
PYTHONPATH=. python examples/fake_sender.py
PYTHONPATH=. python examples/dome_serial.py
PYTHONPATH=. python examples/dome_tcp.py
PYTHONPATH=. python examples/telescope_serial.py
```

The serial and TCP examples require a connected controller. Update the device
path and TCP endpoint before running them.

Every command is created by `TcsPdCommands`. Commands that return structured
data, such as `status_dome()` and `status_ah()`, already include the response
parser, so `Controller.send()` returns the corresponding status object.
