"""Verified REQUIRED fields for HL7 v2 ADT messages.

Each entry is sourced from the official HL7 segment attribute tables (the OPT
column = "R"), cross-referenced via the Caristix HL7-Definition reference at
https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/<segment>. The
human-readable name is stored as data (not just a comment) so it is available
to code, e.g. for user-facing "missing required field" messages.

SCOPE: ADT^A01, HL7 v2.5.1 ONLY. No other event types or versions are covered
yet. See issue #5.
"""

# ADT^A01, HL7 v2.5.1 — fields marked R (required) in the official spec.
# Verified field-by-field against the v2.5.1 segment tables on 2026-06-26.
#
# A01 message structure requires these segments (OPT=R, per the A01 trigger
# event definition): MSH, EVN, PID, PV1. All other segments (SFT, PD1, NK1,
# PV2, AL1, DG1, etc.) are optional and excluded from this R-only table.
ADT_A01_2_5_1_REQUIRED = [
    # --- MSH (Message Header) ---
    {"segment": "MSH", "field": "MSH-1",  "name": "Field Separator"},
    {"segment": "MSH", "field": "MSH-2",  "name": "Encoding Characters"},
    {"segment": "MSH", "field": "MSH-7",  "name": "Date/Time Of Message"},
    {"segment": "MSH", "field": "MSH-9",  "name": "Message Type"},
    {"segment": "MSH", "field": "MSH-10", "name": "Message Control ID"},
    {"segment": "MSH", "field": "MSH-11", "name": "Processing ID"},
    {"segment": "MSH", "field": "MSH-12", "name": "Version ID"},

    # --- EVN (Event Type) ---
    # Note: EVN-1 (Event Type Code) is marked B (backward-compatibility) in
    # v2.5.1, so it is NOT required and is intentionally excluded here.
    {"segment": "EVN", "field": "EVN-2",  "name": "Recorded Date/Time"},

    # --- PID (Patient Identification) ---
    {"segment": "PID", "field": "PID-3",  "name": "Patient Identifier List"},
    # PID-5 is marked R in the spec, BUT hl7apy's STRICT validator does NOT
    # enforce it (a message missing PID-5 still passes validation). We list it
    # here because the spec requires it — our table is the authority, not the
    # validator. See issue #5.
    {"segment": "PID", "field": "PID-5",  "name": "Patient Name"},

    # --- PV1 (Patient Visit) ---
    {"segment": "PV1", "field": "PV1-2",  "name": "Patient Class"},
]
