import numpy as np
import rawpy

# -------------------------
# RAW-domain operations
# -------------------------

def subtract_black(bayer, black, pattern):
    out = bayer.copy()
    for y in range(2):
        for x in range(2):
            c = pattern[y, x]
            out[y::2, x::2] -= black[c]
    return np.clip(out, 0, None)

# -------------------------
# Demosaicing
# -------------------------

def demosaic_libraw(raw):
    rgb = raw.postprocess(
        demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
        no_auto_bright=True,
        gamma=(1, 1),
        output_bps=16,
        use_camera_wb=False   # IMPORTANT: prevent double WB
    ).astype(np.float32)

    return np.ascontiguousarray(
        np.nan_to_num(rgb, nan=0.0, posinf=0.0, neginf=0.0)
    )

def demosaic(raw_ctx, *_):
    return demosaic_libraw(raw_ctx.raw)

# -------------------------
# Color-domain operations
# -------------------------

def apply_wb(bayer, wb, pattern):
    out = bayer.copy()
    for y in range(2):
        for x in range(2):
            c = pattern[y, x]
            out[y::2, x::2] *= wb[c]
    return out

def normalize_exposure(img):
    img = img - img.min()
    m = img.max()
    if m > 1e-6:
        img = img / m
    return img

def gamma_encode(img, gamma):
    if gamma <= 0:
        return img
    img = np.clip(img, 0.0, 1.0)
    return img ** (1.0 / gamma)

# -------------------------
# Visualization helpers
# -------------------------

def normalize(img):
    img = img - img.min()
    return img / max(img.max(), 1e-6)

def draw_bayer_overlay_raw(bayer, pattern):
    h, w = bayer.shape
    rgb = np.zeros((h, w, 3), dtype=np.float32)

    g = normalize(bayer)
    rgb[..., :] = g[..., None]

    for y in range(2):
        for x in range(2):
            c = pattern[y, x]

            # Map LibRaw CFA → RGB index
            if c == 0:      # R
                ch = 0
            elif c == 2:    # B
                ch = 2
            else:           # G1 or G2
                ch = 1

            rgb[y::2, x::2, :] *= 0.3
            rgb[y::2, x::2, ch] = 1.0

    return rgb


def dual_gain_view(bayer):
    low = np.clip(bayer, 0, np.percentile(bayer, 95))
    high = np.clip(bayer - np.percentile(bayer, 30), 0, None)
    return normalize(low + high * 2.0)