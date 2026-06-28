"""Generate a spec-valid ADT^A01 HL7 v2.5.1 message from the required-fields table.

The generator is table-driven: it walks ADT_A01_2_5_1_REQUIRED and produces a
value for each field based on how that field declares it should be populated
(fixed value, weighted coded value, or generated from its datatype).
"""
from __future__ import annotations

import random
from datetime import datetime

from faker import Faker
from hl7apy.core import Message
from hl7apy.validation import Validator

from required_fields import ADT_A01_2_5_1_REQUIRED

from generators import generate_timestamp, generate_string, generate_cx, generate_xpn

from validation import check_required_fields

fake = Faker()

HL7_VERSION = "2.5.1"

# Maps an HL7 datatype to the function that generates a value for it.
DATATYPE_GENERATORS = {
    "TS": generate_timestamp,
    "ST": generate_string,
    "CX": generate_cx,
    "XPN": generate_xpn
}


# --- Value resolution ----------------------------------------------------------

def resolve_value(field: dict) -> str | None:
    """Determine the value for one field entry from the required-fields table.

    Priority: fixed value -> weighted coded value -> datatype-generated.
    Returns None if the datatype has no generator yet (field is skipped).
    """
    if "fixed" in field:
        return field["fixed"]

    if "weighted_values" in field:
        choices = field["weighted_values"]
        codes = [c["code"] for c in choices]
        weights = [c["weight"] for c in choices]
        return random.choices(codes, weights=weights, k=1)[0]

    generator = DATATYPE_GENERATORS.get(field["datatype"])
    if generator is None:
        return None  # datatype not yet supported (e.g. composite CX/XPN)
    return generator()


# --- Message construction ------------------------------------------------------

def set_field(message: Message, field: dict, value: str) -> None:
    """Set a value on the message using the field's segment and HL7 position.

    e.g. field "MSH-7" -> message.msh.msh_7 = value
    """
    segment_name = field["segment"].lower()           # "MSH" -> "msh"
    field_attr = field["field"].replace("-", "_").lower()  # "MSH-7" -> "msh_7"
    segment = getattr(message, segment_name)
    setattr(segment, field_attr, value)


def build_message() -> Message:
    """Build a spec-valid ADT^A01 message from the required-fields table."""
    message = Message("ADT_A01", version=HL7_VERSION)
    for field in ADT_A01_2_5_1_REQUIRED:
        value = resolve_value(field)
        if value is not None:
            set_field(message, field, value)
    check_required_fields(message)   # guarantee completeness before returning
    return message


if __name__ == "__main__":
    msg = build_message()
    Validator.validate(msg)
    required_count = len(ADT_A01_2_5_1_REQUIRED)
    print(f"✓ ADT^A01 (HL7 v2.5.1) — all {required_count} required fields present")
    print()
    print("\n".join(repr(seg) for seg in msg.to_er7().split("\r")))
