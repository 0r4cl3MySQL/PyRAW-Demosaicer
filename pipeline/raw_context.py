import rawpy
import numpy as np

class RawContext:
    def __init__(self, path):
        self.raw = rawpy.imread(path)

        self.bayer = self.raw.raw_image_visible.astype(np.float32)
        self.pattern = self.raw.raw_pattern

        self.black = self.raw.black_level_per_channel
        self.wb = self.raw.camera_whitebalance

        self.rgb_xyz = self.raw.rgb_xyz_matrix
