from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import hashlib
import json

from src.agents.ingest import run_ingest
from src.state import RestorationState


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous Restoration Studio (Phase 1 scaffold)")
    parser.add_argument("--input", required=True, help="Path to an input scan (image file)")
    parser.add_argument("--runs", default="runs", help="Runs output folder (default: runs)")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    runs_root = Path(args.runs).resolve()
    runs_root.mkdir(parents=True, exist_ok=True)

    input_hash = sha256_file(input_path)

    # Create run state + folders
    state = RestorationState.new(input_path=input_path, input_sha256=input_hash, runs_root=runs_root)
    work_dir = Path(state.work_dir)

    # Copy input into run folder for traceability (original remains untouched)
    copied_input = work_dir / "input" / input_path.name
    copied_input.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, copied_input)

    # Define state path BEFORE using it
    state_path = work_dir / "state.json"

    # --- Ingest / Preprocess Agent ---
    state = run_ingest(state, copied_input)

    # Write updated state (includes damage_map_path)
    state.write_json(state_path)


    write_text(work_dir / "README.txt", "Run folder created. Restoration steps will be added in later phases.\n")
    write_text(
        work_dir / "report.json",
        json.dumps(
            {
                "job_id": state.job_id,
                "created_utc": state.created_utc,
                "input": str(input_path),
                "input_sha256": state.input_sha256,
                "status": state.status,
                "note": "Phase 1 scaffold: ingest + preprocess + state manifest.",
            },
            indent=2,
        ),
    )

    print(f"[OK] Created run: {work_dir}")
    print(f"[OK] Copied input: {copied_input}")
    print(f"[OK] Wrote state: {state_path}")
    print(f"[OK] Wrote report: {work_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
