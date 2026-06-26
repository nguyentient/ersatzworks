"""Generate a spec-valid ADT^A01 HL7 v2 message."""

from hl7apy.core import Message
from hl7apy.validation import Validator


def build_adt_a01() -> Message:
    """Build and return a spec-valid ADT^A01 message (HL7 v2.5)."""
    m = Message("ADT_A01", version="2.5")

    # MSH — message header
    m.msh.msh_3 = "ERSATZWORKS"
    m.msh.msh_4 = "ERSATZ_HOSP"
    m.msh.msh_5 = "RECEIVING_APP"
    m.msh.msh_6 = "RECEIVING_FAC"
    m.msh.msh_9 = "ADT^A01^ADT_A01"
    m.msh.msh_10 = "MSG00001"
    m.msh.msh_11 = "T"

    # EVN — event type
    m.evn.evn_2 = "20260625133442"

    # PID — patient identification
    m.pid.pid_3 = "12345678"
    m.pid.pid_5 = "Smith^John"

    # PV1 — patient visit
    m.pv1.pv1_2 = "I"

    return m


if __name__ == "__main__":
    message = build_adt_a01()
    Validator.validate(message)
    print("\n".join(repr(seg) for seg in message.to_er7().split("\r")))
