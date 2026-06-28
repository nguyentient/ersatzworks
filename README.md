# ErsatzWorks

**ErsatzWorks** generates synthetic, non-PHI HL7 v2 ADT messages for testing
healthcare integration pipelines.

Integration engineers constantly need realistic HL7 test data, but real
messages contain protected health information (PHI) and can't be shared freely.
ErsatzWorks produces structurally valid, spec-conformant ADT messages populated
with fake data — safe to use, version-aware, and generated on demand.

> **Status: proof of concept (`0.x`).** ErsatzWorks currently generates
> spec-valid `ADT^A01` admit messages for HL7 **v2.5.1**. The architecture is
> deliberately built to extend to additional event types and versions; see
> [Roadmap](#roadmap).

## How it works

ErsatzWorks is **table-driven**. A verified table of the required fields for a
given event/version (`required_fields.py`) declares each field's HL7 datatype,
length, and how its value is produced — a fixed constant, a weighted coded
value, or generated from its datatype. The generator walks that table and
populates a message, which is built and serialized via
[hl7apy](https://github.com/crs4/hl7apy) and validated against the HL7 v2.5.1
structure.

The required-fields table is **verified against the official HL7 specification**
(segment and trigger-event definitions), not taken from the library alone —
which matters, because the library's validator does not enforce every
spec-required field (e.g. PID-5 Patient Name). The verification methodology is
documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## What it generates

Each run produces a fresh, spec-valid `ADT^A01` message with realistic,
synthetic data:

```
MSH|^~\&|||||20260627195529||ADT^A01^ADT_A01|MSG6239220|T|2.5.1
EVN||20260627195529
PID|||HGG318986^^^ERSATZWORKS^MR||Bowen^Randy
PV1||I

MSH|^~\&|||||20260627195550||ADT^A01^ADT_A01|MSG9329509|T|2.5.1
EVN||20260627195550
PID|||IAC451504^^^ERSATZWORKS^MR||Johnson^Janice^Holly
PV1||E

MSH|^~\&|||||20260627195605||ADT^A01^ADT_A01|MSG0522482|T|2.5.1
EVN||20260627195605
PID|||ABJ274831^^^ERSATZWORKS^MR||Wiley^Hannah
PV1||I
```

Values vary per run: message control IDs and patient identifiers are unique,
patient names are realistically "ragged" (most have a middle initial, some a
full middle name or suffix, many neither), and the patient class is weighted
toward Inpatient with a realistic share of Emergency and Obstetrics admits.

## Why "non-PHI"?

Every generated message is fake by construction — names, identifiers, and dates
are synthetic, and the processing ID is set to `T` (test). No real patient data
is ever produced or required.

## Current capabilities

- `ADT^A01` (Admit/Visit Notification), HL7 v2.5.1
- All 11 spec-required fields populated and verified against the HL7 spec
- Realistic generation: weighted patient class, ragged patient names,
  alphanumeric patient identifiers, current timestamps
- Output validated against the HL7 v2.5.1 structure (STRICT)
- Required-fields presence check: every message is verified complete against
  the spec table before output, catching gaps hl7apy STRICT does not enforce
  (e.g. an empty PID-5)
- HL7 reserved-character escaping: reserved characters appearing inside data
  values are escaped so they cannot corrupt message structure

## Roadmap

- Cross-field logical consistency (e.g. dates in sensible order)
- Additional event types (A03, A08, …) and versions (2.3, 2.7)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, the development
workflow, and the required-field verification methodology.
