"""Value generators for HL7 field datatypes.

Each function takes no arguments and returns a single string value for its HL7
datatype. Composite types (CX, XPN) are assembled as caret-joined strings with
realistic, varied content. Trailing empty components are trimmed.
"""
from __future__ import annotations

import random
from datetime import datetime

from faker import Faker

fake = Faker()

# Name suffixes for XPN (HL7 has no fixed table; these are common values).
SUFFIXES = ["Jr", "Sr", "II", "III"]

# Assigning authority + identifier type for generated patient identifiers (CX).
CX_ASSIGNING_AUTHORITY = "ERSATZWORKS"
CX_ID_TYPE = "MR"  # Medical Record number (HL7 Table 0203)


def escape_hl7(value: str) -> str:
    """Escape the HL7 reserved characters hl7apy does NOT handle on assignment.

    hl7apy already escapes |, ~, and \\ and preserves valid escape sequences, so
    we only handle ^ and & here. Apply to a DATA value BEFORE joining it into a
    composite, so structural separators (added afterward) stay raw.
    """
    value = value.replace("^", "\\S\\")
    value = value.replace("&", "\\T\\")
    return value


def generate_timestamp() -> str:
    """TS — HL7 timestamp in YYYYMMDDHHMMSS format (current time)."""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def generate_string() -> str:
    """ST — a short identifier-style string (used for the message control ID)."""
    return escape_hl7(fake.bothify("MSG#######"))


def generate_cx() -> str:
    """CX — patient identifier: alphanumeric ID with a stable authority/type tail.

    e.g. ABC123456^^^ERSATZWORKS^MR
    """
    patient_id = escape_hl7(fake.bothify("???######").upper())
    return f"{patient_id}^^^{CX_ASSIGNING_AUTHORITY}^{CX_ID_TYPE}"


def generate_xpn() -> str:
    """XPN — patient name with realistic, ragged completeness.

    family + given always present; middle ~60% (mostly an initial); suffix ~8%.
    Trailing empty components are trimmed; internal gaps preserved (e.g. a
    suffix with no middle -> Family^Given^^Suffix).
    """
    family = escape_hl7(fake.last_name())
    given = escape_hl7(fake.first_name())

    middle = ""
    if random.random() < 0.60:               # middle present ~60%
        if random.random() < 0.70:           # of those, ~70% a single initial
            middle = escape_hl7(fake.first_name()[0])
        else:                                 # ~30% a full middle name
            middle = escape_hl7(fake.first_name())

    suffix = random.choice(SUFFIXES) if random.random() < 0.08 else ""

    components = [family, given, middle, suffix]
    while components and components[-1] == "":   # trim trailing empties only
        components.pop()
    return "^".join(components)
