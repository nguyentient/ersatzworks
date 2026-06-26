# Contributing to ErsatzWorks

This project is developed in a team-style workflow even when worked on solo,
so that the history reads as a clear sequence of requirements and the changes
that satisfied them.

## Workflow

1. **Issue first.** Every unit of work starts as a GitHub Issue describing the
   goal and acceptance criteria. The issue is the requirement record.
2. **Feature branch.** Work happens on a short-lived branch named for the work:
   - `feat/<short-name>` for new functionality (e.g. `feat/faker-data`)
   - `fix/<short-name>` for bug fixes
   - `chore/<short-name>` for tooling/maintenance
3. **Pull request.** Open a PR that references the issue with `Closes #N`, so
   merging auto-closes the issue and links requirement to code.
4. **Merge to main.** `main` always holds working, spec-valid code. Delete the
   feature branch after merge.

## Releases & Tagging

- Tags are for **release milestones only**, never for routine pushes.
- When merged work adds up to a meaningful version, tag `main` with `vX.Y.Z`
  following Semantic Versioning (MAJOR.MINOR.PATCH).
- `0.x.y` signals initial development; structure may change between minor
  versions until `1.0.0` declares a stable, relied-upon release.

## Development setup

```powershell
git clone https://github.com/nguyentient/ersatzworks.git
cd ersatzworks
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```