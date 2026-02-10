from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class MaskInfo:
    path: str
    confidence: float


@dataclass
class CandidateInfo:
    path: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoreInfo:
    candidate: str
    fidelity: float
    style: float
    artifact_penalty: float
    final: float
    notes: Optional[str] = None


@dataclass
class RestorationState:
    job_id: str
    created_utc: str
    input_path: str
    input_sha256: str
    work_dir: str
    round: int = 0
    max_rounds: int = 8

    damage_map_path: Optional[str] = None
    masks: List[MaskInfo] = field(default_factory=list)
    candidates: List[CandidateInfo] = field(default_factory=list)
    scores: List[ScoreInfo] = field(default_factory=list)

    winner: Optional[str] = None
    status: str = "running"
    constraints: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def new(input_path: Path, input_sha256: str, runs_root: Path) -> "RestorationState":
        job_id = str(uuid.uuid4())
        work_dir = runs_root / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        return RestorationState(
            job_id=job_id,
            created_utc=utc_now_iso(),
            input_path=str(input_path),
            input_sha256=input_sha256,
            work_dir=str(work_dir),
        )
