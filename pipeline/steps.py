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

def draw_bayer_grid(img, pattern):
    out = img.copy()
    h, w, _ = out.shape

    for y in range(0, h, 2):
        for x in range(0, w, 2):
            c = pattern[y % 2, x % 2]
            color = [(1,0,0),(0,1,0),(0,0,1)][c]
            out[y:y+2, x:x+2] = color

    return out * 0.3 + img * 0.7

def dual_gain_view(bayer):
    low = np.clip(bayer, 0, np.percentile(bayer, 95))
    high = np.clip(bayer - np.percentile(bayer, 30), 0, None)
    return normalize(low + high * 2.0)