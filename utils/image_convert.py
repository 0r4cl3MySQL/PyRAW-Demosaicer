from PyQt6.QtGui import QImage
import numpy as np
import imageio.v2 as imageio

def to_qimage(img: np.ndarray) -> QImage:
    if img.ndim == 2:
        img = img[..., None]

    if img.shape[2] == 1:
        img = np.repeat(img, 3, axis=2)

    img8 = np.clip(img * 255, 0, 255).astype(np.uint8)
    h, w, _ = img8.shape

    # Qt-owned image, 32-bit aligned
    qimg = QImage(w, h, QImage.Format.Format_RGB32)

    # Get writable pointer to ALL image data
    ptr = qimg.bits()
    ptr.setsize(h * qimg.bytesPerLine())

    # Create NumPy view onto Qt memory
    buf = np.frombuffer(ptr, dtype=np.uint8)

    # Reshape as (h, bytesPerLine)
    buf = buf.reshape((h, qimg.bytesPerLine()))

    # Fill image row by row
    # Qt RGB32 on little-endian = BGRA
    buf[:, 0:4*w:4] = img8[:, :, 2]   # B
    buf[:, 1:4*w:4] = img8[:, :, 1]   # G
    buf[:, 2:4*w:4] = img8[:, :, 0]   # R
    buf[:, 3:4*w:4] = 255             # A

    return qimg

def save_image(img, path):
    img8 = (img * 255).astype("uint8")
    imageio.imwrite(path, img8)
