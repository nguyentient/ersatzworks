"""Sequence generation for ErsatzWorks.

A sequence is a correlated set of HL7 messages representing one patient's
journey through a healthcare encounter — e.g. Admit (A01) followed by
Discharge (A03). Messages in a sequence share a PatientRecord (stable patient
and visit identifiers) so they are coherent as a set, not just independent
messages with the same event type.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from generators import generate_cx, generate_xpn, random_past_datetime
from required_fields import get_optional_timestamps


@dataclass
class PatientRecord:
    """Stable patient and visit identifiers shared across a message sequence.

    Generated fresh for the first event in a sequence and carried forward
    unchanged to all subsequent events. Fields here are those whose values
    must be consistent across messages representing the same visit.
    """
    patient_id:    str   # PID-3 — the patient's MRN, stable across the visit
    patient_name:  str   # PID-5 — patient name (stable in A01→A03)
    patient_class: str   # PV1-2 — visit classification, stable across events
    admit_time:    str   # PV1-44 — when the patient was admitted; the temporal
                         #           anchor for the whole sequence


# ---------------------------------------------------------------------------
# VALID_SEQUENCES — explicit allowlist of valid event-order tuples.
# Only sequences listed here are permitted. Callers receive a clear ValueError
# for any combination not in this set — same "fail loud" philosophy as
# get_required_fields. Grows as more event types are added.
# ---------------------------------------------------------------------------
VALID_SEQUENCES: set[tuple[str, ...]] = {
    ("A01", "A03"),   # Admit → Discharge (complete inpatient visit)
}


# ---------------------------------------------------------------------------
# EVENT_LABELS — plain-language names for each event code.
# Used in sequence output headers so readers don't need to know HL7 codes.
# ---------------------------------------------------------------------------
EVENT_LABELS: dict[str, str] = {
    "A01": "Admit",
    "A03": "Discharge",
    "A08": "Update Patient Information",
}


def generate_sequence(
    events: list[str],
    version: str,
) -> list[tuple[str, object]]:
    """Generate a correlated sequence of HL7 messages for one patient visit.

    Validates the requested sequence against VALID_SEQUENCES, creates a
    PatientRecord (stable identifiers shared across all messages), then builds
    each message in order. Admit and discharge timestamps are always included
    in sequence mode — they are structural anchors, not optional fields.

    Returns a list of (event, message) tuples in sequence order.
    Raises ValueError if the sequence is not in VALID_SEQUENCES.
    """
    sequence_key = tuple(events)
    if sequence_key not in VALID_SEQUENCES:
        valid = sorted(VALID_SEQUENCES)
        raise ValueError(
            f"Invalid sequence: {list(events)!r}. "
            f"Valid sequences: {valid}"
        )

    record = _make_patient_record()

    results = []
    for event in events:
        msg = _build_sequence_message(event, version, record)
        results.append((event, msg))

    return results


def _make_patient_record() -> PatientRecord:
    """Generate a fresh PatientRecord for the start of a new sequence.

    The admit_time is generated here as a realistic past timestamp — it becomes
    the temporal anchor for the entire sequence. All subsequent messages use
    this same admit_time rather than generating their own.
    """
    message_time = datetime.now()
    admit_dt = random_past_datetime(before=message_time, max_days_back=5)
    return PatientRecord(
        patient_id=generate_cx(),
        patient_name=generate_xpn(),
        patient_class=random.choices(
            ["I", "E", "B"],
            weights=[90, 8, 2],
            k=1,
        )[0],
        admit_time=admit_dt.strftime("%Y%m%d%H%M%S"),
    )


def _build_sequence_message(
    event: str,
    version: str,
    record: PatientRecord,
) -> object:
    """Build one message in a sequence using the shared PatientRecord.

    Imports build_message here (not at module level) to avoid a circular
    import: generator.py imports sequences.py, so sequences.py cannot import
    generator.py at module level.
    """
    from generator import build_message
    return build_message(
        event=event,
        version=version,
        include_admit=True,
        include_discharge=True,
        record=record,
    )
