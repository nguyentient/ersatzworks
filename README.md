# ErsatzWorks

**ErsatzWorks** generates synthetic, non-PHI HL7 v2 ADT messages for testing
healthcare integration pipelines.

Integration engineers constantly need realistic HL7 test data, but real
messages contain protected health information (PHI) and can't be shared freely.
ErsatzWorks produces structurally valid, spec-conformant ADT messages populated
with fake data — safe to use, version-aware, and generated on demand.

> **Status: proof of concept (`0.x`).** ErsatzWorks currently generates
> spec-valid `ADT^A01` (Admit) and `ADT^A03` (Discharge) messages for HL7
> **v2.5.1**. The architecture is deliberately built to extend to additional
> event types and versions; see [Roadmap](#roadmap).

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

Each run produces a fresh, spec-valid ADT message with realistic, synthetic
data. The event type is selected via `--event` (default: `A01`):

```
python generator.py --event A01
python generator.py --event A03
python generator.py --event A03 --no-admit-time
python generator.py --help
```

**ADT^A01 — Admit/Visit Notification:**

```
MSH|^~\&|||||20260630175534||ADT^A01^ADT_A01|MSG7050095|T|2.5.1
EVN||20260630175534
PID|||YXB694803^^^ERSATZWORKS^MR||Kaufman^Christine^D
PV1||I||||||||||||||||||||||||||||||||||||||||||20260630020357

MSH|^~\&|||||20260630175535||ADT^A01^ADT_A01|MSG2091132|T|2.5.1
EVN||20260630175535
PID|||OOT408345^^^ERSATZWORKS^MR||Hunt^Donald^B
PV1||I||||||||||||||||||||||||||||||||||||||||||20260628155329
```

**ADT^A03 — Discharge/End Visit:**

```
MSH|^~\&|||||20260630175535||ADT^A03^ADT_A03|MSG9590704|T|2.5.1
EVN||20260630175535
PID|||XQW958272^^^ERSATZWORKS^MR||Allen^Anthony^C
PV1||I||||||||||||||||||||||||||||||||||||||||||20260625180216|20260627090216

MSH|^~\&|||||20260630175535||ADT^A03^ADT_A03|MSG4701779|T|2.5.1
EVN||20260630175535
PID|||BOG793643^^^ERSATZWORKS^MR||George^Sharon^Natasha
PV1||I||||||||||||||||||||||||||||||||||||||||||20260629111258|20260701101258
```

In A03 messages, PV1-44 (admit) and PV1-45 (discharge) appear at the end of
the PV1 segment. Discharge is always generated after admit — the relationship
is enforced by construction, not by chance.

Values vary per run: message control IDs and patient identifiers are unique,
patient names are realistically "ragged" (most have a middle initial, some a
full middle name or suffix, many neither), and the patient class is weighted
toward Inpatient with a realistic share of Emergency and Obstetrics.

## Optional timestamps

Admit time (PV1-44) and discharge time (PV1-45) are optional per the HL7 spec
but present in the vast majority of real-world messages. ErsatzWorks includes
them by default; use the flags below to omit them for edge-case testing:

| Flag | Effect |
|---|---|
| `--no-admit-time` | Omit PV1-44 (admit time). Applies to A01 and A03. |
| `--no-discharge-time` | Omit PV1-45 (discharge time). Applies to A03 only. |

## Why "non-PHI"?

Every generated message is fake by construction — names, identifiers, and dates
are synthetic, and the processing ID is set to `T` (test). No real patient data
is ever produced or required.

## Current capabilities

- `ADT^A01` (Admit/Visit Notification) and `ADT^A03` (Discharge/End Visit),
  HL7 v2.5.1
- All spec-required fields populated and verified against the HL7 spec
- Realistic generation: weighted patient class, ragged patient names,
  alphanumeric patient identifiers, current timestamps
- Optional admit/discharge timestamps (PV1-44/45) with cross-field consistency:
  discharge is always generated after admit, enforced by construction
- CLI event selection: `--event`, `--version`, `--no-admit-time`,
  `--no-discharge-time`; run `--help` for full usage
- Output validated against the HL7 v2.5.1 structure (STRICT)
- Required-fields presence check: every message is verified complete against
  the spec table before output, catching gaps hl7apy STRICT does not enforce
  (e.g. an empty PID-5)
- HL7 reserved-character escaping: reserved characters appearing inside data
  values are escaped so they cannot corrupt message structure

## Roadmap

- Cross-field logical consistency for additional fields (e.g. DOB before admit
  time) — partially addressed; further work pending DOB generation
- Additional event types (A08, A11, …) and versions (2.3, 2.7)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, the development
workflow, and the required-field verification methodology.
