# ErsatzWorks

**ErsatzWorks** generates synthetic, non-PHI HL7 v2 ADT messages for testing
healthcare integration pipelines.

Integration engineers constantly need realistic HL7 test data, but real
messages contain protected health information (PHI) and can't be shared freely.
ErsatzWorks produces structurally valid, spec-conformant ADT messages populated
with fake data — safe to use, version-aware, and generated on demand.

## Status

Early development (`0.x`). The engine generates spec-valid `ADT^A01` messages
validated against the HL7 v2.5 structure via [hl7apy](https://github.com/crs4/hl7apy).

## Why "non-PHI"?

Every generated message is fake by construction — names, identifiers, and dates
are synthetic, and the processing ID is set to `T` (test). No real patient data
is ever produced or required.

## Development setup

```powershell
git clone https://github.com/nguyentient/ersatzworks.git
cd ersatzworks
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow.