from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class Histogram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        plt.style.use('dark_background')

        self.fig, self.ax = plt.subplots(figsize=(3, 2))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update(self, img):
        self.ax.clear()
        for c in range(3):
            self.ax.hist(img[..., c].flatten(), bins=256, alpha=0.5)
        self.canvas.draw_idle()
