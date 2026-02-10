# Build Log — Autonomous Restoration Studio

This log tracks the exact steps, decisions, and commands used to bootstrap the repo.

---

## Entry 001 — Repo initialized + published
**Date:** 2026-02-10  
**Local path:** C:\Users\kyler\Documents\GitHub\Agentic\autonomous-restoration-studio  
**Repo:** autonomous-restoration-studio

### Goals
- Create a clean, agent-friendly repo structure
- Make the pipeline bootable (Phase 1)
- Ensure outputs are not committed to git

### Actions completed
- Created README.md describing purpose/scope and “autonomous” definition
- Created full folder tree:
  - docs/, inputs/, runs/, configs/, src/, scripts/, tests/, .github/
  - src/agents/, src/agents/critics/, src/io/, src/utils/, src/pipelines/
- Added placeholders to ensure folders are tracked (e.g. runs/.gitkeep)
- Added Phase 1 runnable scaffold:
  - src/state.py (RestorationState + JSON writing)
  - src/orchestrator.py (creates run folder + copies input + writes state/report)
- Verified pipeline boots via:
  - `python -m src.orchestrator --input inputs\sample_01\original_scan.tif`
- Fixed import issue by running module form:
  - `python -m src.orchestrator` (required so Python recognizes `src` as package)
- Added `src/__init__.py` to formalize package behavior
- Updated `.gitignore` to ignore run outputs:
  - `runs/`

### Key decisions
- Run outputs must never be committed (runs/)
- Keep originals pristine (inputs/) and copy into each run folder for traceability
- Prefer module execution (`python -m`) to avoid import path issues

### Known quirks
- Running `python src/orchestrator.py` causes:
  - `ModuleNotFoundError: No module named 'src'`
- Correct invocation:
  - `python -m src.orchestrator --input <path>`
