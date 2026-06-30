"""Generate spec-valid HL7 v2 ADT messages from the verified required-fields table.

The generator is table-driven: it walks the required-fields table for the
requested event/version and produces a value for each field based on how that
field declares it should be populated (fixed value, weighted coded value, or
generated from its datatype).
"""
from __future__ import annotations

import argparse
import random
from datetime import datetime

from faker import Faker
from hl7apy.core import Message
from hl7apy.validation import Validator

from generators import generate_timestamp, generate_string, generate_cx, generate_xpn, generate_visit_timestamps
from required_fields import get_required_fields, REQUIRED_FIELDS, get_optional_timestamps
from validation import check_required_fields

fake = Faker()
HL7_VERSION = "2.5.1"

# Maps an HL7 datatype to the function that generates a value for it.
DATATYPE_GENERATORS = {
    "TS": generate_timestamp,
    "ST": generate_string,
    "CX": generate_cx,
    "XPN": generate_xpn,
}


# --- Value resolution ---------------------------------------------------------

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
        return None
    return generator()


# --- Message construction ------------------------------------------------------

def set_field(message: Message, field: dict, value: str) -> None:
    """Set a value on the message using the field's segment and HL7 position.

    e.g. field "MSH-7" -> message.msh.msh_7 = value
    """
    segment_name = field["segment"].lower()
    field_attr = field["field"].replace("-", "_").lower()
    segment = getattr(message, segment_name)
    setattr(segment, field_attr, value)


def build_message(
    event: str = "A01",
    version: str = HL7_VERSION,
    include_admit: bool = True,
    include_discharge: bool = True,
) -> Message:
    """Build a spec-valid ADT message for the given event type and version.

    Defaults to ADT^A01 / HL7 v2.5.1 for backward compatibility.
    include_admit / include_discharge control the optional PV1-44/PV1-45
    timestamps (present by default; opt out via the CLI --no-admit-time /
    --no-discharge-time flags). A field is only generated if BOTH the flag
    requests it AND the event/version actually defines it (e.g. A01 has no
    discharge concept regardless of include_discharge).

    Raises ValueError if no required-fields table exists for the combination.
    """
    message_time = datetime.now()
    message = Message(f"ADT_{event}", version=version)

    for field in get_required_fields(event, version):
        value = resolve_value(field)
        if value is not None:
            set_field(message, field, value)

    optional_defs = get_optional_timestamps(event, version)
    want_admit = include_admit and "admit" in optional_defs
    want_discharge = include_discharge and "discharge" in optional_defs

    if want_admit or want_discharge:
        timestamps = generate_visit_timestamps(
            include_admit=want_admit,
            include_discharge=want_discharge,
            message_time=message_time,
        )
        for name, value in timestamps.items():
            set_field(message, optional_defs[name], value)

    check_required_fields(message, event, version)
    return message


if __name__ == "__main__":
    valid_events ={event for event, version in REQUIRED_FIELDS}
    valid_versions = {version for event, version in REQUIRED_FIELDS}

    parser = argparse.ArgumentParser(
        description="Generate a synthetic, non-PHI HL7 v2 ADT message."
    )
    parser.add_argument(
        "--event",
        choices=sorted(valid_events),
        default="A01",
        help="ADT event type to generate (default: A01)",
    )
    parser.add_argument(
        "--version",
        choices=sorted(valid_versions),
        default=HL7_VERSION,
        help=f"HL7 v2 version to use (default: {HL7_VERSION})",
    )
    parser.add_argument(
        "--no-admit-time",
        dest="include_admit",
        action="store_false",
        help="Omit the optional admit time (PV1-44); included by default when the event defines it.",
    )
    parser.add_argument(
        "--no-discharge-time",
        dest="include_discharge",
        action="store_false",
        help="Omit the optional discharge time (PV1-45); included by default when the event defines it.",
    )
    args = parser.parse_args()

    msg = build_message(args.event, args.version, args.include_admit, args.include_discharge)
    Validator.validate(msg)
    required_count = len(get_required_fields(args.event, args.version))
    print(f"✓ ADT^{args.event} (HL7 v{args.version}) — all {required_count} required fields present")
    print()
    print("\n".join(repr(seg) for seg in msg.to_er7().split("\r")))
