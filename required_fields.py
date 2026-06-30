"""Verified required fields for HL7 v2 ADT messages.

Each entry is sourced from the official HL7 segment attribute tables (the OPT
column = "R"), cross-referenced via the Caristix HL7-Definition reference at
https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/<segment>. The
human-readable name is stored as data (not just a comment) so it is available
to code, e.g. for user-facing "missing required field" messages.

Each entry also records how its value is produced:
  - "fixed": a literal value to use as-is.
  - "weighted_values": a coded value set with weights for realistic random
    selection (code/desc/weight dicts).
  - otherwise: the value is generated from the field's "datatype".

STRUCTURE: REQUIRED_FIELDS is keyed by (event, version) tuple. Each value is
the full list of required fields for that event/version, composed from the
shared base fields plus the event-specific MSH-9. Access via
get_required_fields(event, version).

Verified event/version pairs:
  - ADT^A01, HL7 v2.5.1 — verified 2026-06-26
  - ADT^A03, HL7 v2.5.1 — verified 2026-06-28
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Shared base — required fields common to all ADT events (HL7 v2.5.1).
# MSH-9 (Message Type) is intentionally excluded; it is event-specific and
# added per-event in REQUIRED_FIELDS below.
# Verified field-by-field against the v2.5.1 segment tables on 2026-06-26.
#
# A01 and A03 message structure requires these segments (OPT=R, per their
# trigger-event definitions): MSH, EVN, PID, PV1. All other segments are
# optional and excluded from this R-only table.
# ---------------------------------------------------------------------------
_ADT_2_5_1_BASE: list[dict] = [
    # --- MSH (Message Header) — all required fields except MSH-9 ---
    {"segment": "MSH", "field": "MSH-1",  "name": "Field Separator",         "datatype": "ST",  "length": 1,   "fixed": "|"},
    {"segment": "MSH", "field": "MSH-2",  "name": "Encoding Characters",     "datatype": "ST",  "length": 4,   "fixed": "^~\\&"},
    {"segment": "MSH", "field": "MSH-7",  "name": "Date/Time Of Message",    "datatype": "TS",  "length": 26},
    {"segment": "MSH", "field": "MSH-10", "name": "Message Control ID",      "datatype": "ST",  "length": 20},
    {"segment": "MSH", "field": "MSH-11", "name": "Processing ID",           "datatype": "PT",  "length": 3,   "fixed": "T"},
    {"segment": "MSH", "field": "MSH-12", "name": "Version ID",              "datatype": "VID", "length": 60,  "fixed": "2.5.1"},
    # --- EVN (Event Type) ---
    # EVN-1 (Event Type Code) is marked B (backward-compatibility) in v2.5.1
    # and is intentionally excluded.
    {"segment": "EVN", "field": "EVN-2",  "name": "Recorded Date/Time",      "datatype": "TS",  "length": 26},
    # --- PID (Patient Identification) ---
    # PID-3 (CX, composite) — generated as alphanumeric ID with stable
    # assigning-authority/type tail. See generators.generate_cx.
    {"segment": "PID", "field": "PID-3",  "name": "Patient Identifier List", "datatype": "CX",  "length": 250},
    # PID-5 (XPN, composite) — generated as ragged patient name. Marked R in
    # the spec, but hl7apy's STRICT validator does NOT enforce it (see issue
    # #5), so our table remains the authority. See generators.generate_xpn.
    {"segment": "PID", "field": "PID-5",  "name": "Patient Name",            "datatype": "XPN", "length": 250},
    # --- PV1 (Patient Visit) ---
    # PV1-2 is a coded field (HL7 Table 0004). ADT events do not pin a single
    # class; real feeds are mostly Inpatient with some Emergency / Obstetrics,
    # so we weight a realistic distribution.
    {"segment": "PV1", "field": "PV1-2",  "name": "Patient Class",           "datatype": "IS",  "length": 1,
     "weighted_values": [
         {"code": "I", "desc": "Inpatient",  "weight": 90},
         {"code": "E", "desc": "Emergency",  "weight": 8},
         {"code": "B", "desc": "Obstetrics", "weight": 2},
     ]},
]


# ---------------------------------------------------------------------------
# REQUIRED_FIELDS — keyed by (event, version) tuple.
# Each value is the full required-fields table for that pair, composed as
# the shared base + the event-specific MSH-9 entry. MSH-9 is appended last;
# set_field addresses by field name (not position), so order is irrelevant
# to generation correctness.
# ---------------------------------------------------------------------------
REQUIRED_FIELDS: dict[tuple[str, str], list[dict]] = {
    ("A01", "2.5.1"): _ADT_2_5_1_BASE + [
        {"segment": "MSH", "field": "MSH-9", "name": "Message Type",
         "datatype": "MSG", "length": 15, "fixed": "ADT^A01^ADT_A01"},
    ],
    ("A03", "2.5.1"): _ADT_2_5_1_BASE + [
        {"segment": "MSH", "field": "MSH-9", "name": "Message Type",
         "datatype": "MSG", "length": 15, "fixed": "ADT^A03^ADT_A03"},
    ],
}


def get_required_fields(event: str, version: str) -> list[dict]:
    """Return the verified required-fields table for an event/version pair.

    Raises ValueError if no table exists for the requested combination —
    so callers get a clear error rather than a bare KeyError.
    """
    key = (event, version)
    if key not in REQUIRED_FIELDS:
        raise ValueError(
            f"No required-fields table for event={event!r}, version={version!r}. "
            f"Available: {sorted(REQUIRED_FIELDS)}"
        )
    return REQUIRED_FIELDS[key]

# ---------------------------------------------------------------------------
# OPTIONAL_TIMESTAMPS — keyed by (event, version) tuple.
# Each value is a dict mapping a logical name ("admit", "discharge") to its
# field metadata. Distinct from REQUIRED_FIELDS: these are user-controlled
# (CLI opt-out flags), not always generated, and some have relationships to
# each other (discharge depends on admit when both are present — see
# generators.generate_visit_timestamps).
# ---------------------------------------------------------------------------
OPTIONAL_TIMESTAMPS: dict[tuple[str, str], dict[str, dict]] = {
    ("A01", "2.5.1"): {
        "admit": {"segment": "PV1", "field": "PV1-44", "name": "Admit Date/Time", "datatype": "TS", "length": 26},
    },
    ("A03", "2.5.1"): {
        "admit":     {"segment": "PV1", "field": "PV1-44", "name": "Admit Date/Time",     "datatype": "TS", "length": 26},
        "discharge": {"segment": "PV1", "field": "PV1-45", "name": "Discharge Date/Time", "datatype": "TS", "length": 26},
    },
}


def get_optional_timestamps(event: str, version: str) -> dict[str, dict]:
    """Return the optional-timestamp field definitions for an event/version.

    Returns an empty dict if the event/version has no optional timestamps
    defined (rather than raising — absence of optional fields is normal,
    unlike absence of a required-fields table).
    """
    return OPTIONAL_TIMESTAMPS.get((event, version), {})
