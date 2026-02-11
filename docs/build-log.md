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

### Entry 002 — Added Ingest Agent + Segmentation Agent
**Date:** 2026-02-10
**Local path:** C:\Users\kyler\Documents\GitHub\autonomous-restoration-studio
**Repo:** autonomous-restoration-studio

#### What changed

Added Agent 1 ingest/preprocess (src/agents/ingest.py)

Added Agent 2 segmentation (src/agents/segment.py)

Tuned segmentation (edge smoothing + 2% margin wipe)

Wired agents into orchestrator (ingest → segment → state write)

Installed dependencies: opencv-python, numpy

Key commands used

python -m src.orchestrator --input inputs\sample_01\original_scan_42.jpg

python -m pip install opencv-python numpy

Any findstr checks you used

Gotchas fixed

python src/orchestrator.py import failure → use python -m ...

state_path defined after usage → moved before

stray ] / indentation errors

cleaned not defined → replaced make_foreground_mask with known-good version

Quality notes

Mask preview showed “ants on border” → margin wipe helped

That’s the “how we got here” record.

2) SOURCES.md — add the LoC item + IIIF URL

Add a bullet like:

Library of Congress plate 43 page: (LoC page link)

IIIF image: (tile URL)

Local input file name: inputs/sample_01/original_scan_42.jpg

Note: pct:50 prototype

(You already created inputs/sample_01/source.txt — this is the repo-wide index.)

3) docs/restoration-journal.md — log the run + outcomes

One short section:

Input: original_scan_42.jpg

Outputs created:

preprocess: normalized.png, damage_map.png

segment: mask.png, mask_preview.png

Observation: segmentation mostly correct, border artifacts noted

4) GitHub commits — make sure they’re cleanly segmented

If you haven’t yet, make sure you have commits roughly like:

Add ingest/preprocess agent (v0)

Add segmentation agent (v0)

Tune segmentation mask smoothing + border suppression

Wire background cleanup agent (when you finish that edit)

Clean commits = easier to roll back when something “helpful” breaks later.

5) Optional but worth it: add “Run outputs are ignored” note

In README.md or docs/architecture.md, add a single sentence:

runs/ is generated output and is gitignored.