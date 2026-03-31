# Symmetry Detection For 2D Human Skeleton Sequences

This note summarizes principled approaches for bilateral arm-symmetry quantification in 2D landmark time series, why they matter, and high-level computation logic.

## Problem Framing

In dance/tutorial motion, symmetry is often phase-dependent:
- one-arm-leading sections can be intentionally asymmetric,
- mirrored shapes can be symmetric even when raw coordinates differ by sign,
- bilateral coordination can include temporal lag,
- pauses and very short segments make correlation unstable.

A practical symmetry pipeline should therefore combine multiple complementary metrics rather than one raw correlation number.

## Approaches Considered

### 1) Windowed Speed Correlation

Motivation:
- Captures whether both arms speed up and slow down together in local time.

High-level logic:
- Compute left/right wrist speed time series.
- For each local time window, compute Pearson correlation.
- Output in range [-1, 1].

Strength:
- Easy to interpret.

Limitation:
- Sensitive to lag and undefined on short/constant windows.

### 2) Lag-Aware Local Correlation

Motivation:
- Bilateral motion can be coordinated but offset by a few frames.

High-level logic:
- For each local window, test multiple lags in [-L, +L].
- Compute correlation for each lag where valid.
- Keep the best correlation as lag-aware synchrony.

Strength:
- More robust to lead-lag patterns.

Limitation:
- Can overestimate synchrony if lag range is too large.

### 3) Coactivation Index (Amplitude Overlap)

Motivation:
- Distinguishes one-arm-dominant vs both-arm-active segments.

High-level logic:
- Given left and right speed magnitudes:
- coactivation = 2 * min(L, R) / (L + R + eps)
- Output in [0, 1].

Strength:
- Low for unilateral motion, high for bilateral motion.

Limitation:
- Ignores direction and geometry.

### 4) Extension Similarity

Motivation:
- Symmetry should include comparable limb reach, not just speed synchrony.

High-level logic:
- Compute per-arm extension magnitudes (wrist relative to shoulder).
- similarity = 1 - |L_ext - R_ext| / (L_ext + R_ext + eps)
- Output in [0, 1].

Strength:
- Directly geometry-aware.

Limitation:
- Same extension can still correspond to different arm directions.

### 5) Mirror-Angle Congruence (Geometric)

Motivation:
- Bilateral symmetry in the image plane is mirror symmetry.

High-level logic:
- Convert each arm vector (shoulder -> wrist) to angle.
- Mirror left-arm x before angle comparison.
- Use wrapped angular difference d in [0, pi].
- congruence = 1 - d / pi.

Strength:
- Explicitly models mirror geometry.

Limitation:
- Requires reliable shoulder-relative vectors.

### 6) Elbow-Angle Similarity (Geometric Joint Factor)

Motivation:
- Symmetric arm shapes involve similar joint configurations.

High-level logic:
- Compute elbow angle per arm from shoulder-elbow-wrist triplets.
- similarity = 1 - |theta_left - theta_right| / pi.
- Output in [0, 1].

Strength:
- Uses articulation, not just endpoint motion.

Limitation:
- Sensitive to elbow landmark noise/occlusion.

### 7) Signed Dominance (Asymmetry Direction)

Motivation:
- Helpful for detecting left-leading vs right-leading passages.

High-level logic:
- dominance = (R - L) / (R + L + eps) using speed magnitudes.
- Output in [-1, 1].

Strength:
- Encodes asymmetry direction and magnitude.

Limitation:
- Not a symmetry score by itself.

## Recommended Composite Interpretation

Use multiple tracks together:
- Synchrony: local + lag-aware correlation.
- Bilateral activation: coactivation.
- Geometric mirror quality: mirror-angle congruence.
- Shape similarity: extension and elbow-angle similarity.
- Asymmetry side: signed dominance.

This combination better captures transitions like:
- left-only movement,
- right-only movement,
- then both-arm synchronized movement.

## Implementation Notes In This Repository

Current symmetry chart output includes:
- local correlation,
- lag-aware correlation,
- coactivation,
- extension similarity,
- mirror-angle congruence,
- elbow-angle similarity (when elbow landmarks are available),
- signed dominance.

Outputs are produced per song as:
- `<clip>_symmetry.pdf` (under the `symmetry/` analysis subfolder)
