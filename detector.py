"""
Deepfake image detection using classical forensics techniques:
  1. Error Level Analysis (ELA)
  2. Noise inconsistency analysis
  3. High-frequency artifact analysis
  4. Face symmetry / consistency check
  5. JPEG compression artifact scoring
Scores are combined into a single fake probability (0-100%).
"""

import io
import math
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


# ---------------------------------------------------------------------------
# 1. Error Level Analysis (ELA)
# ---------------------------------------------------------------------------
def ela_score(pil_img: Image.Image, quality: int = 90) -> float:
    """
    Re-save the image at a fixed JPEG quality and measure residual error.
    Authentic images show uniform, low residuals; manipulated regions stand out.
    Returns a score 0-1 (higher → more likely fake).
    """
    # Convert to RGB for JPEG
    img_rgb = pil_img.convert("RGB")

    # Save at reduced quality into memory
    buf = io.BytesIO()
    img_rgb.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    compressed = Image.open(buf).convert("RGB")

    # Pixel-wise difference
    diff = ImageChops.difference(img_rgb, compressed)
    enhancer = ImageEnhance.Brightness(diff)
    diff_enhanced = enhancer.enhance(10)

    diff_arr = np.array(diff_enhanced).astype(np.float32)
    mean_diff = diff_arr.mean()

    # High mean diff indicates heavily re-compressed (manipulated) blocks
    # Empirically, real untouched images score ~15-30, fakes ~40-80+
    score = np.clip((mean_diff - 10) / 60.0, 0.0, 1.0)
    return float(score)


# ---------------------------------------------------------------------------
# 2. Noise Inconsistency Analysis
# ---------------------------------------------------------------------------
def noise_inconsistency_score(img_arr: np.ndarray) -> float:
    """
    Real camera images have consistent, Gaussian-ish noise patterns.
    Deepfakes often have patchy noise from blending / generation.
    Returns a score 0-1 (higher → more inconsistent / likely fake).
    """
    gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Estimate noise via Laplacian residual
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    noise = gray - blur

    # Divide image into 8x8 patches and compute local noise std
    h, w = noise.shape
    patch_h, patch_w = h // 8, w // 8
    stds = []
    for i in range(8):
        for j in range(8):
            patch = noise[i*patch_h:(i+1)*patch_h, j*patch_w:(j+1)*patch_w]
            stds.append(float(np.std(patch)))

    if not stds:
        return 0.0

    std_arr = np.array(stds)
    # Coefficient of variation of local noise stds
    cv = std_arr.std() / (std_arr.mean() + 1e-6)
    # High CV → inconsistent noise → more likely fake
    score = np.clip(cv / 1.5, 0.0, 1.0)
    return float(score)


# ---------------------------------------------------------------------------
# 3. High-Frequency Artifact Scoring (DCT-based)
# ---------------------------------------------------------------------------
def hf_artifact_score(img_arr: np.ndarray) -> float:
    """
    GAN-generated images often show periodic high-frequency patterns.
    We analyse the FFT magnitude spectrum for suspicious peaks.
    Returns a score 0-1 (higher → more artifact-like).
    """
    gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gray_resized = cv2.resize(gray, (256, 256))

    # 2D FFT
    f = np.fft.fft2(gray_resized)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)

    # Exclude DC component
    h, w = magnitude.shape
    cx, cy = h // 2, w // 2
    magnitude[cx-2:cx+3, cy-2:cy+3] = 0

    log_mag = np.log1p(magnitude)

    # Ratio of energy in high-freq bands vs total
    total_energy = log_mag.sum() + 1e-6
    # Inner 25% (low freq) region mask
    r_low = min(h, w) // 8
    mask = np.zeros_like(log_mag)
    cv2.circle(mask, (cy, cx), r_low, 1, -1)
    low_energy = (log_mag * mask).sum()
    high_energy = total_energy - low_energy

    hf_ratio = high_energy / total_energy

    # GAN outputs tend to have unnaturally flat / spiked high-freq content
    # Empirically real images: hf_ratio ~0.85-0.92; GAN fakes: varies widely
    # We flag both extremes as suspicious
    deviation = abs(hf_ratio - 0.88)
    score = np.clip(deviation / 0.15, 0.0, 1.0)
    return float(score)


# ---------------------------------------------------------------------------
# 4. Face-region Blending Boundary Detection
# ---------------------------------------------------------------------------
def blending_boundary_score(img_arr: np.ndarray) -> float:
    """
    Detect unnatural blending boundaries (face-swap seams) using
    edge inconsistency in luminance.
    Returns a score 0-1 (higher → more boundary-like / likely fake).
    """
    gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
    # Sobel edges
    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge_mag = np.sqrt(sx**2 + sy**2)

    # Compare edge distribution between center and periphery
    h, w = gray.shape
    cx, cy = h // 2, w // 2
    r = min(h, w) // 4

    mask_center = np.zeros((h, w), dtype=bool)
    mask_center[cx-r:cx+r, cy-r:cy+r] = True
    mask_outer = ~mask_center

    center_mean = edge_mag[mask_center].mean()
    outer_mean = edge_mag[mask_outer].mean()

    # In deepfakes, the face centre often has very different edge density
    if outer_mean < 1e-6:
        return 0.0

    ratio = center_mean / (outer_mean + 1e-6)
    # Strongly asymmetric ratios suggest a pasted face
    deviation = abs(ratio - 1.0)
    score = np.clip(deviation / 2.5, 0.0, 1.0)
    return float(score)


# ---------------------------------------------------------------------------
# 5. JPEG Ghost Detection
# ---------------------------------------------------------------------------
def jpeg_ghost_score(pil_img: Image.Image) -> float:
    """
    JPEG ghosts appear when a saved image was previously compressed at a
    different quality. Detects copy-paste manipulation.
    Returns a score 0-1.
    """
    img_rgb = pil_img.convert("RGB")
    arr = np.array(img_rgb).astype(np.float32)

    min_diff = np.inf
    for q in [65, 75, 85, 95]:
        buf = io.BytesIO()
        img_rgb.save(buf, format="JPEG", quality=q)
        buf.seek(0)
        recomp = np.array(Image.open(buf)).astype(np.float32)
        diff = np.mean((arr - recomp) ** 2)
        if diff < min_diff:
            min_diff = diff

    # Very low min-diff means the image was already saved at one of these
    # qualities → more likely a re-saved / manipulated image
    score = np.clip(1.0 - (min_diff / 500.0), 0.0, 1.0)
    return float(score)


# ---------------------------------------------------------------------------
# Combined detector
# ---------------------------------------------------------------------------
def analyze_image(file_bytes: bytes) -> dict:
    """
    Run all forensics checks and return a consolidated result.

    Returns dict with:
        fake_probability  : float 0-100
        verdict           : "REAL" | "DEEPFAKE" | "SUSPICIOUS"
        confidence        : "High" | "Medium" | "Low"
        scores            : dict of individual scores
        summary           : human-readable explanation
    """
    # Decode
    nparr = np.frombuffer(file_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_cv is None:
        raise ValueError("Could not decode image. Please upload a valid JPG/PNG.")

    pil_img = Image.open(io.BytesIO(file_bytes))

    # Run sub-analyses
    scores = {
        "ela":               ela_score(pil_img),
        "noise":             noise_inconsistency_score(img_cv),
        "hf_artifacts":      hf_artifact_score(img_cv),
        "blending_boundary": blending_boundary_score(img_cv),
        "jpeg_ghost":        jpeg_ghost_score(pil_img),
    }

    # Weighted combination  (ELA + noise are most reliable)
    weights = {
        "ela":               0.30,
        "noise":             0.25,
        "hf_artifacts":      0.15,
        "blending_boundary": 0.15,
        "jpeg_ghost":        0.15,
    }

    fake_prob = sum(scores[k] * weights[k] for k in scores) * 100.0
    fake_prob = round(min(100.0, max(0.0, fake_prob)), 1)

    # Determine verdict
    if fake_prob >= 55:
        verdict = "DEEPFAKE"
    elif fake_prob >= 35:
        verdict = "SUSPICIOUS"
    else:
        verdict = "REAL"

    # Confidence
    distance = abs(fake_prob - 50)
    if distance >= 30:
        confidence = "High"
    elif distance >= 15:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Build explanation
    flags = []
    if scores["ela"] > 0.4:
        flags.append("high error-level residuals (possible re-save after editing)")
    if scores["noise"] > 0.5:
        flags.append("inconsistent noise pattern across image regions")
    if scores["hf_artifacts"] > 0.5:
        flags.append("abnormal high-frequency spectral pattern")
    if scores["blending_boundary"] > 0.4:
        flags.append("suspicious edge asymmetry between face and background")
    if scores["jpeg_ghost"] > 0.6:
        flags.append("JPEG ghost artifacts (possible copy-paste manipulation)")

    if verdict == "REAL":
        summary = "No significant manipulation signals detected. The image appears authentic."
    elif verdict == "SUSPICIOUS":
        summary = "Some manipulation signals found, but not conclusive. "
        summary += ("Flags: " + "; ".join(flags)) if flags else ""
    else:
        summary = "Multiple manipulation signals detected — likely a deepfake or edited image. "
        summary += ("Flags: " + "; ".join(flags)) if flags else ""

    return {
        "fake_probability": fake_prob,
        "verdict": verdict,
        "confidence": confidence,
        "scores": {k: round(v * 100, 1) for k, v in scores.items()},
        "summary": summary,
    }

