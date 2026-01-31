from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt
from pipeline.steps import *
from utils.image_convert import to_qimage, save_image
from ui.image_view import ImageView
from ui.histogram import Histogram

class MainWindow(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self._last_px = (-1, -1)
        self.ctx = ctx
        self.stage = 0
        self.gamma = 2.2
        self.show_bayer = False
        self.show_dual_gain = False
        self.image = None

        self.view = ImageView()
        self.hist = Histogram()
        self.hist.setFixedHeight(250)  # or any value that fits your U
        self.info = QLabel()

        # Controls
        self.stage_btn = QPushButton("Next stage")
        self.stage_btn.clicked.connect(self.next_stage)

        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(10, 40)
        self.gamma_slider.setValue(22)
        self.gamma_slider.valueChanged.connect(self.update_pipeline)
        # Start disabled (stage < 5)
        self.gamma_slider.setEnabled(False)


        self.bayer_cb = QCheckBox("Bayer overlay")
        self.bayer_cb.stateChanged.connect(self.toggle_bayer)

        self.dual_cb = QCheckBox("Dual-gain view")
        self.dual_cb.stateChanged.connect(self.toggle_dual)

        self.save_btn = QPushButton("Save stage")
        self.save_btn.clicked.connect(self.save_stage)

        self.stage_label = QLabel()

        self.demosaic_mode = "AHD"

        controls = QHBoxLayout()
        controls.addWidget(self.stage_btn)
        controls.addWidget(QLabel("Gamma"))
        controls.addWidget(self.gamma_slider)
        controls.addWidget(self.bayer_cb)
        controls.addWidget(self.dual_cb)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.stage_label)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.view)
        layout.addWidget(self.info)
        layout.addWidget(self.hist)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.view.pixelHovered.connect(self.inspect_pixel)
        self.update_pipeline()

    def next_stage(self):
        self.stage = (self.stage + 1) % 6
        self.update_pipeline()

    def toggle_bayer(self, s):
        self.show_bayer = s > 0
        self.update_pipeline()

    def toggle_dual(self, s):
        self.show_dual_gain = s > 0
        self.update_pipeline()

    def update_pipeline(self):
        self.view.blockSignals(True)

        STAGE_NAMES = [
            "Raw Bayer",
            "Black level subtracted",
            "White balance enabled",
            "Demosaiced",
            "Normalized",
            "Gamma corrected",
        ]

        self.stage_label.setText(
            f"Stage {self.stage}: {STAGE_NAMES[self.stage]}"
        )

        self.gamma_slider.setEnabled(self.stage >= 5)

        # --- RAW DOMAIN ---
        bayer = self.ctx.bayer.astype(float)

        if self.stage >= 1:
            bayer = subtract_black(bayer, self.ctx.black, self.ctx.pattern)

        # WHITE BALANCE IN RAW DOMAIN
        if self.stage >= 2:
            bayer = apply_wb(bayer, self.ctx.wb, self.ctx.pattern)

        if self.show_dual_gain:
            bayer = dual_gain_view(bayer)

        if self.stage >= 3:
            rgb = demosaic(self.ctx, bayer, self.demosaic_mode)

            rgb = np.clip(rgb, 0.0, None)

        else:
            rgb = normalize(bayer)

        # --- NORMALIZATION (GLOBAL) ---
        if self.stage >= 4:
            rgb = normalize_exposure(rgb)

        # --- GAMMA ---
        if self.stage >= 5:
            gamma = self.gamma_slider.value() / 10.0
            rgb = gamma_encode(rgb, gamma)

        # --- DISPLAY NORMALIZATION ---
        rgb = normalize_exposure(rgb)

        if self.show_bayer and rgb.ndim == 3:
            rgb = draw_bayer_grid(rgb, self.ctx.pattern)

        self.image = rgb.copy()
        self.view.setImage(to_qimage(self.image))
        self.hist.update(self.image)

        self.view.blockSignals(False)

    def inspect_pixel(self, x, y):
        if self.image is None:
            return

        if (x, y) == self._last_px:
            return
        self._last_px = (x, y)

        shape = self.image.shape

        if len(shape) == 2:
            h, w = shape
            if not (0 <= x < w and 0 <= y < h):
                return

            v = float(self.image[y, x])
            self.info.setText(
                f"x={x} y={y}  V={v:.4f}"
            )

        elif len(shape) >= 3:
            h, w = shape[:2]
            if not (0 <= x < w and 0 <= y < h):
                return

            pixel = self.image[y, x]

            if len(pixel) >= 3:
                r, g, b = map(float, pixel[:3])
                self.info.setText(
                    f"x={x} y={y}  R={r:.4f} G={g:.4f} B={b:.4f}"
                )
            else:
                v = float(pixel[0])
                self.info.setText(
                    f"x={x} y={y}  V={v:.4f}"
                )

    def save_stage(self):
        save_image(self.image, f"stage_{self.stage}.png")
