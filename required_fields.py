"""Verified REQUIRED fields for HL7 v2 ADT messages.

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
    {"segment": "MSH", "field": "MSH-1",  "name": "Field Separator",         "datatype": "ST",  "length": 1,   "fixed": "|"},
    {"segment": "MSH", "field": "MSH-2",  "name": "Encoding Characters",     "datatype": "ST",  "length": 4,   "fixed": "^~\\&"},
    {"segment": "MSH", "field": "MSH-7",  "name": "Date/Time Of Message",    "datatype": "TS",  "length": 26},
    {"segment": "MSH", "field": "MSH-9",  "name": "Message Type",            "datatype": "MSG", "length": 15,  "fixed": "ADT^A01^ADT_A01"},
    {"segment": "MSH", "field": "MSH-10", "name": "Message Control ID",      "datatype": "ST",  "length": 20},
    {"segment": "MSH", "field": "MSH-11", "name": "Processing ID",           "datatype": "PT",  "length": 3,   "fixed": "T"},
    {"segment": "MSH", "field": "MSH-12", "name": "Version ID",              "datatype": "VID", "length": 60,  "fixed": "2.5.1"},

    # --- EVN (Event Type) ---
    # Note: EVN-1 (Event Type Code) is marked B (backward-compatibility) in
    # v2.5.1, so it is NOT required and is intentionally excluded here.
    {"segment": "EVN", "field": "EVN-2",  "name": "Recorded Date/Time",      "datatype": "TS",  "length": 26},

    # --- PID (Patient Identification) ---
    # PID-3 (CX, composite) — generated as an alphanumeric ID with a stable
    # assigning-authority/type tail. See generators.generate_cx.
    {"segment": "PID", "field": "PID-3",  "name": "Patient Identifier List", "datatype": "CX",  "length": 250},
    # PID-5 (XPN, composite) — generated as a ragged patient name. Marked R in
    # the spec, but hl7apy's STRICT validator does NOT enforce it (see issue #5),
    # so our table remains the authority. See generators.generate_xpn.
    {"segment": "PID", "field": "PID-5",  "name": "Patient Name",            "datatype": "XPN", "length": 250},

    # --- PV1 (Patient Visit) ---
    # PV1-2 is a coded field (HL7 Table 0004). A01 does not pin a single class;
    # real feeds are mostly Inpatient with some Emergency / Obstetrics, so we
    # weight a realistic distribution rather than hardcoding one value.
    {"segment": "PV1", "field": "PV1-2",  "name": "Patient Class",           "datatype": "IS",  "length": 1,
     "weighted_values": [
         {"code": "I", "desc": "Inpatient",  "weight": 90},
         {"code": "E", "desc": "Emergency",  "weight": 8},
         {"code": "B", "desc": "Obstetrics", "weight": 2},
     ]},
]
