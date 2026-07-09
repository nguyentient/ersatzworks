# ErsatzWorks

**ErsatzWorks** generates synthetic, non-PHI HL7 v2 ADT messages for testing
healthcare integration pipelines.

Integration engineers constantly need realistic HL7 test data, but real
messages contain protected health information (PHI) and can't be shared freely.
ErsatzWorks produces structurally valid, spec-conformant ADT messages populated
with fake data — safe to use, version-aware, and generated on demand.

> **Status: proof of concept (`0.x`).** ErsatzWorks currently generates
> spec-valid `ADT^A01` (Admit) and `ADT^A03` (Discharge) messages for HL7
> **v2.5.1**, as standalone messages or correlated patient-journey sequences.
> The architecture is deliberately built to extend to additional event types
> and versions; see [Roadmap](#roadmap).

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

ErsatzWorks produces clean, copy-pasteable HL7 messages — ready to drop into
any integration tool or flat file. Generate a single event or a correlated
patient-journey sequence:

```
python generator.py                              # single A01 (default)
python generator.py --event A03                  # single A03
python generator.py --sequence A01 A03           # correlated journey
python generator.py --event A01 --no-dob         # edge-case testing
python generator.py --help                       # full usage
```

**Single message — ADT^A01 (Admit/Visit Notification):**

```
MSH|^~\&|||||20260709080534||ADT^A01^ADT_A01|MSG0694051|T|2.5.1
EVN||20260709080534
PID|||LKK104030^^^ERSATZWORKS^MR||Casey^Leah^P^III||19810421|F
PV1||I||||||||||||||||||||||||||||||||||||||||||20260706090456
```

**Single message — ADT^A03 (Discharge/End Visit):**

```
MSH|^~\&|||||20260709080535||ADT^A03^ADT_A03|MSG0254480|T|2.5.1
EVN||20260709080535
PID|||XDY368024^^^ERSATZWORKS^MR||Singleton^Adrian||19380411|M
PV1||B||||||||||||||||||||||||||||||||||||||||||20260706130430|20260707230430
```

**Sequence — complete patient journey (A01 → A03):**

```
--- Admit (ADT^A01) ---
MSH|^~\&|||||20260709080535||ADT^A01^ADT_A01|MSG1872874|T|2.5.1
EVN||20260709080535
PID|||JLY786815^^^ERSATZWORKS^MR||Murphy^Douglas^S^II||20250910|M
PV1||I||||||||||||||||||||||||||||||||||||||||||20260708100532

--- Discharge (ADT^A03) ---
MSH|^~\&|||||20260709080535||ADT^A03^ADT_A03|MSG0797576|T|2.5.1
EVN||20260709080535
PID|||JLY786815^^^ERSATZWORKS^MR||Murphy^Douglas^S^II||20250910|M
PV1||I||||||||||||||||||||||||||||||||||||||||||20260708100532|20260709040532
```

In a sequence, patient identifiers (MRN, name, patient class), DOB, gender,
and admit time are shared across all messages — the A03 discharge time is
always generated after the A01 admit time, enforced by construction. Each
message gets its own unique message control ID.

In the PID segment, positions 7 and 8 carry DOB (`YYYYMMDD`) and
Administrative Sex (`M`/`F`/`U`/`O`). Given names are gender-correlated —
male patients get male names, female patients get female names.

Values vary per run: message control IDs and patient identifiers are unique,
patient names are realistically "ragged" (most have a middle initial, some a
full middle name or suffix, many neither), and the patient class is weighted
toward Inpatient with a realistic share of Emergency and Obstetrics.

## Optional fields

The following fields are optional per the HL7 spec but present in the vast
majority of real-world messages. ErsatzWorks includes them by default; use
the flags below to omit them for edge-case testing. All flags are single
message only — in sequence mode these fields are always included.

| Flag | Field | Effect |
|---|---|---|
| `--no-admit-time` | PV1-44 | Omit admit time. Applies to A01 and A03. |
| `--no-discharge-time` | PV1-45 | Omit discharge time. Applies to A03 only. |
| `--no-dob` | PID-7 | Omit date of birth. Applies to A01 and A03. |
| `--no-gender` | PID-8 | Omit administrative sex. Applies to A01 and A03. |

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
- Optional admit/discharge timestamps (PV1-44/45): discharge always generated
  after admit, enforced by construction
- Optional demographics (PID-7/8): DOB always generated before admit time
  (enforced by construction); given names are gender-correlated
- Correlated sequence generation (`--sequence A01 A03`): shared patient
  identifiers, DOB, gender, and consistent timestamps across a complete
  patient journey
- CLI: `--event`, `--version`, `--sequence`, `--no-admit-time`,
  `--no-discharge-time`, `--no-dob`, `--no-gender`; run `--help` for full usage
- Output validated against the HL7 v2.5.1 structure (STRICT)
- Required-fields presence check: every message is verified complete against
  the spec table before output, catching gaps hl7apy STRICT does not enforce
  (e.g. an empty PID-5)
- HL7 reserved-character escaping: reserved characters appearing inside data
  values are escaped so they cannot corrupt message structure

## Roadmap

- Mutation sequences (e.g. A01 → A08 demographic update)
- Additional event types (A08, A11, …) and versions (2.3, 2.7)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, the development
workflow, and the required-field verification methodology.
