from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.state import RestorationState


def normalize_image(img_bgr: np.ndarray) -> np.ndarray:
    # Convert to LAB and equalize L channel for gentle normalization
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_eq = cv2.equalizeHist(l)
    lab_eq = cv2.merge((l_eq, a, b))
    norm = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
    return norm


def estimate_damage_map(img_bgr: np.ndarray) -> np.ndarray:
    # Heuristic damage map: highlights yellowed paper + noise as proxy
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Paper yellowing proxy: low-frequency illumination gradient
    blur = cv2.GaussianBlur(gray, (51, 51), 0)
    illum_diff = cv2.absdiff(gray, blur)

    # Noise proxy: high-frequency components
    edges = cv2.Canny(gray, 50, 150)

    # Combine heuristics
    damage = cv2.normalize(illum_diff + edges, None, 0, 255, cv2.NORM_MINMAX)
    return damage


def run_ingest(state: RestorationState, input_image_path: Path) -> RestorationState:
    work_dir = Path(state.work_dir)
    out_dir = work_dir / "preprocess"
    out_dir.mkdir(parents=True, exist_ok=True)

    img_bgr = cv2.imread(str(input_image_path))
    if img_bgr is None:
        raise ValueError(f"Could not read image: {input_image_path}")

    normalized = normalize_image(img_bgr)
    damage_map = estimate_damage_map(img_bgr)

    norm_path = out_dir / "normalized.png"
    dmg_path = out_dir / "damage_map.png"

    cv2.imwrite(str(norm_path), normalized)
    cv2.imwrite(str(dmg_path), damage_map)

    # Update state
    state.damage_map_path = str(dmg_path)

    return state
