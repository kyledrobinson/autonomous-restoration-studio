from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.state import RestorationState


def load_mask(mask_path: Path, target_shape: tuple[int, int]) -> np.ndarray:
    m = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Could not read mask: {mask_path}")
    if m.shape[:2] != target_shape:
        m = cv2.resize(m, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)
    return m


def feather_mask(mask_fg: np.ndarray, radius: int = 9) -> np.ndarray:
    # mask_fg: 255 = foreground, 0 = background
    # returns soft alpha where 1.0 means keep original (fg), 0.0 means use cleaned (bg)
    m = mask_fg.astype(np.float32) / 255.0
    k = radius if radius % 2 == 1 else radius + 1
    m = cv2.GaussianBlur(m, (k, k), 0)
    return np.clip(m, 0.0, 1.0)


def run_background_clean(state: RestorationState, input_image_path: Path) -> RestorationState:
    work_dir = Path(state.work_dir)
    out_dir = work_dir / "restore"
    out_dir.mkdir(parents=True, exist_ok=True)

    img_bgr = cv2.imread(str(input_image_path))
    if img_bgr is None:
        raise ValueError(f"Could not read image: {input_image_path}")

    if not state.masks:
        raise ValueError("No masks found in state. Run segmentation first.")

    # Use most recent mask
    mask_path = Path(state.masks[-1].path)
    mask_fg = load_mask(mask_path, img_bgr.shape[:2])

    # Background = inverse of foreground
    bg = (mask_fg == 0)

    # Work in LAB to reduce yellowing in background only
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)

    # Estimate paper "B" channel median in background (yellow/blue axis)
    b_bg = B[bg]
    b_med = float(np.median(b_bg)) if b_bg.size > 1000 else float(np.median(B))

    # Pull background B channel toward neutral (128)
    target_b = 128.0
    strength = 0.55  # 0..1, higher = more de-yellow
    B_adj = B.copy()
    B_adj[bg] = B[bg] + (target_b - b_med) * strength

    # Gentle background denoise on L channel only
    L_u8 = np.clip(L, 0, 255).astype(np.uint8)
    L_dn = cv2.fastNlMeansDenoising(L_u8, None, h=6, templateWindowSize=7, searchWindowSize=21).astype(np.float32)

    L_adj = L.copy()
    L_adj[bg] = L_dn[bg]

    lab2 = cv2.merge([L_adj, A, B_adj])
    cleaned_bgr = cv2.cvtColor(np.clip(lab2, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

    # Blend with feathered mask to avoid harsh boundaries
    alpha_fg = feather_mask(mask_fg, radius=13)  # 1=fg keep original, 0=bg use cleaned
    alpha_fg_3 = np.dstack([alpha_fg, alpha_fg, alpha_fg])

    blended = (
        img_bgr.astype(np.float32) * alpha_fg_3
        + cleaned_bgr.astype(np.float32) * (1.0 - alpha_fg_3)
    ).astype(np.uint8)

    out_clean = out_dir / "background_clean.png"
    out_delta = out_dir / "background_delta.png"

    cv2.imwrite(str(out_clean), blended)

    delta = cv2.absdiff(img_bgr, blended)
    cv2.imwrite(str(out_delta), delta)

    return state
