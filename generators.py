"""Value generators for HL7 field datatypes.

Each function takes no arguments and returns a single string value for its HL7
datatype. Composite types (CX, XPN) are assembled as caret-joined strings with
realistic, varied content. Trailing empty components are trimmed.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

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


def random_past_datetime(before: datetime, max_days_back: int = 5) -> datetime:
    """Return a random datetime within max_days_back days before `before`.

    Used to generate realistic-but-bounded past timestamps (e.g. admit time,
    or a standalone discharge time) without drifting implausibly far back.
    """
    seconds_back = random.randint(0, max_days_back * 24 * 60 * 60)
    return before - timedelta(seconds=seconds_back)


def generate_visit_timestamps(
    include_admit: bool,
    include_discharge: bool,
    message_time: datetime,
    admit_time: str | None = None,
) -> dict[str, str]:
    """Generate admit/discharge timestamps (PV1-44/PV1-45) respecting their
    real-world relationship.

    - Admit alone: a realistic past timestamp, admit <= message_time.
    - Discharge alone (no admit): a realistic past timestamp, independent.
    - Both: discharge = admit + a random duration (2-48 hours), guaranteeing
      discharge >= admit BY CONSTRUCTION.
    - admit_time provided (sequence mode): skips admit generation and uses
      the provided value as the anchor for discharge. The record's admit time
      carries forward from the A01 rather than being regenerated.

    KNOWN SIMPLIFICATION: the admit-discharge duration range is flat and does
    not vary by patient class (PV1-2). Making duration depend on patient class
    is a deliberate future refinement, not handled here.

    Returns a dict with "admit" and/or "discharge" keys (HL7 TS strings) for
    whichever were requested.
    """
    result = {}
    admit_dt = None

    if admit_time is not None:
        from datetime import datetime as dt
        admit_dt = dt.strptime(admit_time, "%Y%m%d%H%M%S")
        result["admit"] = admit_time
    elif include_admit:
        admit_dt = random_past_datetime(before=message_time, max_days_back=5)
        result["admit"] = admit_dt.strftime("%Y%m%d%H%M%S")

    if include_discharge:
        if admit_dt is not None:
            duration = timedelta(hours=random.randint(2, 48))
            discharge_dt = admit_dt + duration
        else:
            discharge_dt = random_past_datetime(before=message_time, max_days_back=5)
        result["discharge"] = discharge_dt.strftime("%Y%m%d%H%M%S")

    return result


def generate_demographics(
    include_dob: bool,
    include_gender: bool,
    admit_time: str,
) -> dict[str, str]:
    """Generate optional demographic fields (PID-7/PID-8) with correlation.

    Gender is rolled first, then DOB is generated relative to admit_time
    (guaranteeing DOB < admit by construction). Returns a dict with "dob"
    and/or "gender" keys for whichever were requested.

    Gender weighting reflects realistic patient population distribution:
      M (Male)     ~49%
      F (Female)   ~49%
      U (Unknown)  ~1.5%
      O (Other)    ~0.5%

    DOB: a random date 0-90 years before admit_time, formatted YYYYMMDD.
    """
    result = {}

    gender_value = None
    if include_gender:
        gender_value = random.choices(
            ["M", "F", "U", "O"],
            weights=[49, 49, 1.5, 0.5],
            k=1,
        )[0]
        result["gender"] = gender_value

    if include_dob:
        admit_dt = datetime.strptime(admit_time, "%Y%m%d%H%M%S")
        days_back = random.randint(0, 90 * 365)
        dob_dt = admit_dt - timedelta(days=days_back)
        result["dob"] = dob_dt.strftime("%Y%m%d")

    return result


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


def generate_xpn(gender: str | None = None) -> str:
    """XPN — patient name with realistic, ragged completeness.

    family + given always present; middle ~60% (mostly an initial); suffix ~8%.
    Trailing empty components are trimmed; internal gaps preserved (e.g. a
    suffix with no middle -> Family^Given^^Suffix).

    gender: when provided, selects a gender-appropriate given name (M ->
    first_name_male, F -> first_name_female, others -> first_name). Default
    None uses the gender-neutral generator — preserving existing behavior.
    """
    family = escape_hl7(fake.last_name())

    if gender == "M":
        given = escape_hl7(fake.first_name_male())
    elif gender == "F":
        given = escape_hl7(fake.first_name_female())
    else:
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
