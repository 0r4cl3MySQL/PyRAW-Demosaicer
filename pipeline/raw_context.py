import rawpy
import numpy as np


class RawContext:
    def __init__(self, path):
        self.raw = rawpy.imread(path)

        # -------------------------
        # RAW image & Bayer pattern
        # -------------------------
        self.bayer = self.raw.raw_image_visible.astype(np.float32)
        self.pattern = np.asarray(self.raw.raw_pattern, dtype=np.int32)

        # -------------------------
        # Black levels (per channel)
        # LibRaw order: R, G1, B, G2
        # -------------------------
        self.black = np.asarray(
            self.raw.black_level_per_channel,
            dtype=np.float32
        )

        # -------------------------
        # White balance (camera)
        # LibRaw order: R, G1, B, G2
        # Normalize to green
        # -------------------------
        wb = np.asarray(
            self.raw.camera_whitebalance,
            dtype=np.float32
        )

        # Safety: avoid divide-by-zero
        if wb[1] > 0:
            wb /= wb[1]

        self.wb = wb

        # -------------------------
        # Color correction matrix
        # LibRaw may give 3x4, 4x3, or 3x3
        # We sanitize to 3x3 or None
        # -------------------------

        XYZ_TO_SRGB = np.array([
            [3.2406, -1.5372, -0.4986],
            [-0.9689, 1.8758, 0.0415],
            [0.0557, -0.2040, 1.0570],
        ], dtype=np.float32)

        m = self.raw.rgb_xyz_matrix

        if m is None:
            self.ccm = None
        else:
            m = np.asarray(m, dtype=np.float32)

            if m.shape == (3, 4):
                cam_to_xyz = m[:, :3]
            elif m.shape == (4, 3):
                cam_to_xyz = m[:3, :]
            elif m.shape == (3, 3):
                cam_to_xyz = m
            else:
                print("WARNING: unexpected rgb_xyz_matrix shape:", m.shape)
                cam_to_xyz = None

            if cam_to_xyz is None:
                self.ccm = None
            else:
                self.ccm = XYZ_TO_SRGB @ cam_to_xyz
