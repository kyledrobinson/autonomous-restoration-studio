from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.state import RestorationState


def hex_to_bgr(hex_str: str) -> tuple[int, int, int]:
    s = hex_str.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"Expected 6-char hex like f2eee4, got: {hex_str}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (b, g, r)


def load_mask(mask_path: Path, target_shape: tuple[int, int]) -> np.ndarray:
    m = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Could not read mask: {mask_path}")
    if m.shape[:2] != target_shape:
        m = cv2.resize(m, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)
    return m


def _border_band_mask(h: int, w: int, border_pct: float) -> np.ndarray:
    band = int(min(h, w) * border_pct)
    band = max(2, band)
    m = np.zeros((h, w), dtype=np.uint8)
    m[:band, :] = 255
    m[-band:, :] = 255
    m[:, :band] = 255
    m[:, -band:] = 255
    return m


def run_border_fix(
    state: RestorationState,
    base_image_path: Path,
    mode: str = "fill",
    fill_hex: str = "f2eee4",
    border_pct: float = 0.06,
    crop_pct: float = 0.04,
) -> RestorationState:
    """
    mode="fill": replace border band with solid paper tone, feathered inward, while protecting foreground mask
    mode="crop": crop fixed % from each edge
    """
    work_dir = Path(state.work_dir)
    out_dir = work_dir / "restore"
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(base_image_path))
    if img is None:
        raise ValueError(f"Could not read image: {base_image_path}")

    h, w = img.shape[:2]

    if mode.lower() == "crop":
        dx = int(w * crop_pct)
        dy = int(h * crop_pct)
        cropped = img[dy : h - dy, dx : w - dx].copy()
        out_path = out_dir / "border_crop.png"
        cv2.imwrite(str(out_path), cropped)
        return state

    # default: fill
    if not state.masks:
        raise ValueError("No masks found in state. Run segmentation first.")

    fg_mask_path = Path(state.masks[-1].path)
    fg = load_mask(fg_mask_path, (h, w))  # 255=foreground
    border = _border_band_mask(h, w, border_pct)  # 255=in border band

    # Don't touch the artwork: remove FG from border region
    border[fg > 0] = 0

    # Feather the border mask so the fill blends inward
    # Convert border mask -> alpha (0..1)
    k = 31  # feather width; must be odd
    if k % 2 == 0:
        k += 1
    alpha = (border.astype(np.float32) / 255.0)
    alpha = cv2.GaussianBlur(alpha, (k, k), 0)
    alpha = np.clip(alpha, 0.0, 1.0)
    alpha3 = np.dstack([alpha, alpha, alpha])

    fill_bgr = np.zeros_like(img, dtype=np.uint8)
    fill_bgr[:, :] = hex_to_bgr(fill_hex)

    blended = (img.astype(np.float32) * (1.0 - alpha3) + fill_bgr.astype(np.float32) * alpha3).astype(np.uint8)

    out_path = out_dir / "border_fill.png"
    cv2.imwrite(str(out_path), blended)
    return state
