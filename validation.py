"""Validation for generated HL7 messages.

Checks generated messages against the verified required-fields table — our own
authority, independent of hl7apy's validator (which does not enforce every
spec-required field). Currently covers required-field presence; will grow to
cover more validation concerns over time.
"""
from __future__ import annotations

from hl7apy.core import Message

from exceptions import MissingRequiredFieldError
from required_fields import ADT_A01_2_5_1_REQUIRED


def find_missing_required_fields(message: Message) -> list[dict]:
    """Return the required-field entries that are absent or empty in the message.

    A field is considered missing if its value is an empty string. Returns an
    empty list if all required fields are present.
    """
    missing = []
    for field in ADT_A01_2_5_1_REQUIRED:
        segment = getattr(message, field["segment"].lower())
        field_attr = field["field"].replace("-", "_").lower()
        value = getattr(segment, field_attr).value
        if value == "":
            missing.append(field)
    return missing


def check_required_fields(message: Message) -> None:
    """Raise MissingRequiredFieldError if any required field is missing/empty.

    Does nothing (returns None) if all required fields are present.
    """
    missing = find_missing_required_fields(message)
    if missing:
        raise MissingRequiredFieldError(missing)
