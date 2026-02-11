from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.state import RestorationState


def hex_to_lab(hex_str: str) -> np.ndarray:
    s = hex_str.strip().lstrip("#")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    bgr = np.uint8([[[b, g, r]]])
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
    return lab  # L,A,B


def band_median_lab(lab: np.ndarray, side: str, offset: int, band: int) -> np.ndarray:
    h, w = lab.shape[:2]
    if side == "top":
        y0 = offset
        y1 = min(h, offset + band)
        patch = lab[y0:y1, :, :]
    elif side == "bottom":
        y1 = h - offset
        y0 = max(0, y1 - band)
        patch = lab[y0:y1, :, :]
    elif side == "left":
        x0 = offset
        x1 = min(w, offset + band)
        patch = lab[:, x0:x1, :]
    elif side == "right":
        x1 = w - offset
        x0 = max(0, x1 - band)
        patch = lab[:, x0:x1, :]
    else:
        raise ValueError(side)

    return np.median(patch.reshape(-1, 3), axis=0).astype(np.float32)


def delta_e_simple(a: np.ndarray, b: np.ndarray) -> float:
    # Not true DeltaE2000, but good enough for thresholding paper tone proximity
    return float(np.linalg.norm(a - b))


def run_auto_crop_paper(
    state: RestorationState,
    base_image_path: Path,
    target_hex: str = "f2eee4",
    band_px: int = 24,
    step_px: int = 8,
    threshold: float = 10.0,
    safety_margin_px: int = 12,
    max_crop_pct: float = 0.18,
) -> RestorationState:
    """
    Crops inward from each side until the edge band median LAB is close to the target paper tone.
    """
    work_dir = Path(state.work_dir)
    out_dir = work_dir / "restore"
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(base_image_path))
    if img is None:
        raise ValueError(f"Could not read image: {base_image_path}")

    h, w = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    target = hex_to_lab(target_hex)

    max_crop_x = int(w * max_crop_pct)
    max_crop_y = int(h * max_crop_pct)

    offsets = {}
    for side, max_crop in [("top", max_crop_y), ("bottom", max_crop_y), ("left", max_crop_x), ("right", max_crop_x)]:
        offset = 0
        while offset < max_crop:
            med = band_median_lab(lab, side, offset, band_px)
            if delta_e_simple(med, target) <= threshold:
                break
            offset += step_px
        offsets[side] = offset

    x0 = offsets["left"] + safety_margin_px
    x1 = w - offsets["right"] - safety_margin_px
    y0 = offsets["top"] + safety_margin_px
    y1 = h - offsets["bottom"] - safety_margin_px

    # Clamp
    x0 = max(0, min(x0, w - 2))
    y0 = max(0, min(y0, h - 2))
    x1 = max(x0 + 1, min(x1, w))
    y1 = max(y0 + 1, min(y1, h))

    cropped = img[y0:y1, x0:x1].copy()

    out_path = out_dir / "auto_crop.png"
    cv2.imwrite(str(out_path), cropped)

    return state
