from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.state import RestorationState, MaskInfo


def make_foreground_mask(img_bgr: np.ndarray) -> np.ndarray:
    """
    Heuristic v0:
    - Convert to LAB
    - Use L channel to separate darker ink/paint from lighter paper
    - Clean with morphology
    - Keep large connected components (foreground artwork)
    Returns a uint8 mask: 255 = foreground, 0 = background
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)

    # Adaptive threshold on luminance: artwork tends to be darker than paper
    thr = cv2.adaptiveThreshold(
        L,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        51,
        7,
    )

    # Remove tiny specks and fill small gaps
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(thr, cv2.MORPH_OPEN, k, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, k, iterations=2)

    # Keep only reasonably sized components (drops paper noise)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)

    mask = np.zeros_like(cleaned)
    h, w = cleaned.shape[:2]
    min_area = int((h * w) * 0.0005)  # 0.05% of image area

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            mask[labels == i] = 255

    # Final smoothing pass to reduce jagged edges
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2, iterations=1)

    # Suppress page border artifacts by zeroing a thin margin
    h, w = mask.shape[:2]
    margin = int(min(h, w) * 0.02)  # 2% border
    mask[:margin, :] = 0
    mask[-margin:, :] = 0
    mask[:, :margin] = 0
    mask[:, -margin:] = 0

    return mask




def overlay_mask(img_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Green overlay on foreground."""
    overlay = img_bgr.copy()
    green = np.zeros_like(img_bgr)
    green[:, :] = (0, 255, 0)

    alpha = 0.25
    fg = mask.astype(bool)
    overlay[fg] = (overlay[fg] * (1 - alpha) + green[fg] * alpha).astype(np.uint8)
    return overlay


def run_segment(state: RestorationState, input_image_path: Path) -> RestorationState:
    work_dir = Path(state.work_dir)
    out_dir = work_dir / "segment"
    out_dir.mkdir(parents=True, exist_ok=True)

    img_bgr = cv2.imread(str(input_image_path))
    if img_bgr is None:
        raise ValueError(f"Could not read image: {input_image_path}")

    mask = make_foreground_mask(img_bgr)

    mask_path = out_dir / "mask.png"
    preview_path = out_dir / "mask_preview.png"

    cv2.imwrite(str(mask_path), mask)
    cv2.imwrite(str(preview_path), overlay_mask(img_bgr, mask))

    # Update state (keep multiple masks later; for now just append one)
    state.masks.append(MaskInfo(path=str(mask_path), confidence=0.60))
    return state
