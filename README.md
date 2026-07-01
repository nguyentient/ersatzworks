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
python generator.py                          # single A01 (default)
python generator.py --event A03             # single A03
python generator.py --sequence A01 A03      # correlated journey
python generator.py --event A01 --no-admit-time   # edge-case testing
python generator.py --help                  # full usage
```

**Single message — ADT^A01 (Admit/Visit Notification):**

```
MSH|^~\&|||||20260701153418||ADT^A01^ADT_A01|MSG0808402|T|2.5.1
EVN||20260701153418
PID|||UGZ048527^^^ERSATZWORKS^MR||Olsen^Kevin
PV1||I||||||||||||||||||||||||||||||||||||||||||20260701024942
```

**Single message — ADT^A03 (Discharge/End Visit):**

```
MSH|^~\&|||||20260701153418||ADT^A03^ADT_A03|MSG3533836|T|2.5.1
EVN||20260701153418
PID|||YRC325057^^^ERSATZWORKS^MR||Love^Thomas
PV1||I||||||||||||||||||||||||||||||||||||||||||20260627044611|20260629034611
```

**Sequence — complete patient journey (A01 → A03):**

```
--- Admit (ADT^A01) ---
MSH|^~\&|||||20260701153418||ADT^A01^ADT_A01|MSG8428078|T|2.5.1
EVN||20260701153418
PID|||BTM736255^^^ERSATZWORKS^MR||Coffey^Samantha^M
PV1||I||||||||||||||||||||||||||||||||||||||||||20260628190150

--- Discharge (ADT^A03) ---
MSH|^~\&|||||20260701153418||ADT^A03^ADT_A03|MSG2518983|T|2.5.1
EVN||20260701153418
PID|||BTM736255^^^ERSATZWORKS^MR||Coffey^Samantha^M
PV1||I||||||||||||||||||||||||||||||||||||||||||20260628190150|20260629100150
```

In a sequence, patient identifiers (MRN, name, patient class) and admit time
are shared across all messages — the A03 discharge time is always generated
after the A01 admit time, enforced by construction. Each message gets its own
unique message control ID.

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
| `--no-admit-time` | Omit PV1-44 (admit time). Applies to A01 and A03. Single message only. |
| `--no-discharge-time` | Omit PV1-45 (discharge time). Applies to A03 only. Single message only. |

These flags are not valid with `--sequence` — timestamps are structural in a
sequence and always included.

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
- Correlated sequence generation (`--sequence A01 A03`): shared patient
  identifiers and consistent timestamps across a complete patient journey
- CLI: `--event`, `--version`, `--sequence`, `--no-admit-time`,
  `--no-discharge-time`; run `--help` for full usage
- Output validated against the HL7 v2.5.1 structure (STRICT)
- Required-fields presence check: every message is verified complete against
  the spec table before output, catching gaps hl7apy STRICT does not enforce
  (e.g. an empty PID-5)
- HL7 reserved-character escaping: reserved characters appearing inside data
  values are escaped so they cannot corrupt message structure

## Roadmap

- Mutation sequences (e.g. A01 → A08 demographic update)
- Cross-field logical consistency for additional fields (e.g. DOB before admit
  time) — partially addressed; further work pending DOB generation
- Additional event types (A08, A11, …) and versions (2.3, 2.7)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, the development
workflow, and the required-field verification methodology.
