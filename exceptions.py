"""Custom exceptions for ErsatzWorks.

Defining these in one place lets callers catch ErsatzWorks-specific failures
distinctly from ordinary Python errors. As the project's validation grows
(additional event types, versions, and validation concerns), further exception
types will live here.
"""
from __future__ import annotations


class MissingRequiredFieldError(Exception):
    """Raised when a generated message is missing one or more required fields.

    Indicates a generation defect: the message-building logic failed to populate
    a field the verified required-fields table marks as required. The message is
    NOT returned — generation halts so the defect surfaces rather than emitting
    an incomplete message.
    """

    def __init__(self, missing: list[dict]) -> None:
        self.missing = missing
        names = ", ".join(f"{f['field']} ({f['name']})" for f in missing)
        super().__init__(f"Missing required field(s): {names}")
