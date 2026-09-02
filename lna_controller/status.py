from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TcsPdStatus:
    address: str
    raw: str
    value: str = ""
    alarm: bool = False
    attention: bool = False
    error: bool = False
    busy: bool = False
    fields: dict[str, bool | str] | None = None

    @property
    def initialized(self) -> bool:
        return bool(self.value.strip())

    @property
    def tag(self) -> int | None:
        if self.address not in {"CUP", "MEADE"} or not self.value.strip():
            return None
        try:
            return int(self.value)
        except ValueError:
            return None


def _parse_status(raw: str, address: str) -> TcsPdStatus:
    text = raw.replace("\r", "")
    flags = {
        "alarm": _bit(text, 13),
        "attention": _bit(text, 14),
        "error": _bit(text, 15),
        "busy": _bit(text, 16),
    }
    fields: dict[str, bool | str] = {}
    if address in {"AH", "DEC"}:
        fields.update(
            protection=_bit(text, 17),
            tracking=_bit(text, 19),
            variable_tracking=_bit(text, 20),
            fast=_bit(text, 21),
            slow=_bit(text, 22),
            fine=_bit(text, 23),
            run=_bit(text, 24),
            motor=_bit(text, 25),
            indexer_ready=_bit(text, 26),
            manual=_bit(text, 27),
        )
        value = text[1:12] if len(text) >= 12 else ""
    elif address in {"CUP", "MEADE"}:
        fields.update(
            platform_down=_bit(text, 17),
            lcb_on=_bit(text, 18),
            slit_open=_bit(text, 19),
            windscreen_down=_bit(text, 20),
            run=_bit(text, 24),
            slit_moving=_bit(text, 26),
            slit_closed=_bit(text, 27),
            slit_open_sensor=_bit(text, 28),
        )
        value = text[8:11] if len(text) >= 11 else ""
    elif address == "TUBO":
        fields.update(
            mirror_abc=text[10] if len(text) > 10 else "",
            ventilator=_bit(text, 11),
            mirror3_stopped=_bit(text, 17),
            mirror3_cassegrain=_bit(text, 18),
            focus_moving=_bit(text, 19),
            secondary_cassegrain=_bit(text, 20),
            mechanism_2_moving=_bit(text, 21),
            mechanism_3_moving=_bit(text, 22),
            mechanism_4_moving=_bit(text, 23),
            calibration_mirror_limit=_bit(text, 24),
            he_lamp=_bit(text, 25),
            neon_lamp=_bit(text, 26),
            return_relay=_bit(text, 27),
            calibration_relay=_bit(text, 28),
        )
        value = text[0:10]
    else:
        value = text[1:12] if len(text) >= 12 else ""
    return TcsPdStatus(
        address=address,
        raw=text,
        value=value,
        fields=fields,
        **flags,
    )


class TcsPdStatusParser:
    def __init__(self, address: str = "MEADE"):
        if address not in {"JIGA", "AH", "DEC", "TUBO", "CUP", "ECASS", "COUDE", "MEADE"}:
            raise ValueError(f"Unsupported address: {address}")
        self.address = address

    def __call__(self, raw: str) -> TcsPdStatus:
        return _parse_status(raw, self.address)


def _bit(text: str, index: int) -> bool:
    return len(text) > index and text[index] == "1"
