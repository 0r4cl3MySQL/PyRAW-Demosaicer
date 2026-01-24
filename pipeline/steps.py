import numpy as np
import cv2
import rawpy

def subtract_black(bayer, black, pattern):
    out = bayer.copy()
    for y in range(2):
        for x in range(2):
            c = pattern[y, x]
            out[y::2, x::2] -= black[c]
    return np.clip(out, 0, None)


def apply_wb(bayer, wb, pattern):
    out = bayer.copy()
    for y in range(2):
        for x in range(2):
            c = pattern[y, x]
            out[y::2, x::2] *= wb[c]
    return out


def demosaic_bilinear(bayer, pattern):

    pattern = np.asarray(pattern, dtype=int)
    pattern[pattern == 3] = 1  # normalize G2 → G

    pat = tuple(map(tuple, pattern))

    code_map = {
        ((0,1),(1,2)): cv2.COLOR_BAYER_RG2RGB,
        ((2,1),(1,0)): cv2.COLOR_BAYER_BG2RGB,
        ((1,0),(2,1)): cv2.COLOR_BAYER_GR2RGB,
        ((1,2),(0,1)): cv2.COLOR_BAYER_GB2RGB,
    }

    if pat not in code_map:
        raise ValueError(f"Unsupported Bayer pattern: {pat}")

    h, w = bayer.shape
    if h % 2 or w % 2:
        bayer = bayer[:h - h % 2, :w - w % 2]

    b = np.ascontiguousarray(
        np.clip(bayer, 0, 65535).astype(np.uint16, copy=False)
    )

    rgb = cv2.cvtColor(b, code_map[pat]).astype(np.float32)
    rgb = normalize_rgb(rgb)
    return rgb

def demosaic_libraw(raw):
    rgb = raw.postprocess(
        demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
        no_auto_bright=True,
        gamma=(1, 1),
        output_bps=16,
        use_camera_wb=True
    ).astype(np.float32)

    # SAME SAFETY RULES
    rgb = np.nan_to_num(rgb, nan=0.0, posinf=0.0, neginf=0.0)
    rgb = normalize(rgb)
    rgb = np.ascontiguousarray(rgb)

    return rgb

def normalize(img):
    img = img - img.min()
    return img / max(img.max(), 1e-6)


def gamma_encode(img, gamma):
    if gamma <= 0:
        return img
    img = np.clip(img, 0.0, 1.0)
    return img ** (1.0 / gamma)

def draw_bayer_grid(img, pattern):
    out = img.copy()
    h, w, _ = out.shape

    for y in range(0, h, 2):
        for x in range(0, w, 2):
            c = pattern[y % 2, x % 2]
            color = [(1,0,0),(0,1,0),(0,0,1)][c]
            out[y:y+2, x:x+2] = color

    return out * 0.3 + img * 0.7

def demosaic(raw_ctx, bayer, mode):
    if mode == "AHD":
        return demosaic_libraw(raw_ctx.raw)

    return demosaic_bilinear(bayer, raw_ctx.pattern)

def dual_gain_view(bayer):
    low = np.clip(bayer, 0, np.percentile(bayer, 95))
    high = np.clip(bayer - np.percentile(bayer, 30), 0, None)
    return normalize(low + high * 2.0)

# Emphasize chroma differences
def demosaic_error_view(rgb):

    r, g, b = rgb[...,0], rgb[...,1], rgb[...,2]

    err_rg = np.abs(r - g)
    err_bg = np.abs(b - g)

    error = np.stack([
        err_rg,
        err_bg,
        np.zeros_like(err_rg)
    ], axis=2)

    return normalize(error * 5.0)

def dual_gain_curve(bayer, t):
    low = bayer
    high = np.clip(bayer - t, 0, None) * 2.0
    return normalize(low + high)

def normalize_rgb(rgb):
    out = rgb.copy()
    for c in range(3):
        ch = out[..., c]
        ch = ch - ch.min()
        m = ch.max()
        if m > 1e-6:
            ch /= m
        out[..., c] = ch
    return out

def apply_wb_rgb(rgb, wb):
    out = rgb.copy()
    out[..., 0] *= wb[0]  # R
    out[..., 1] *= wb[1]  # G
    out[..., 2] *= wb[2]  # B
    return out