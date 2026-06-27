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

fake = Faker()

HL7_VERSION = "2.5.1"


# --- Datatype value generators -------------------------------------------------
# Each takes no arguments and returns a single string value for its HL7 datatype.

def generate_timestamp() -> str:
    """TS — HL7 timestamp in YYYYMMDDHHMMSS format (current time)."""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def generate_string() -> str:
    """ST — a short identifier-style string (used for the message control ID)."""
    return fake.bothify("MSG#######")


# Maps an HL7 datatype to the function that generates a value for it.
# Extended in later work (e.g. CX, XPN composite types).
DATATYPE_GENERATORS = {
    "TS": generate_timestamp,
    "ST": generate_string,
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
    return message


if __name__ == "__main__":
    msg = build_message()
    Validator.validate(msg)
