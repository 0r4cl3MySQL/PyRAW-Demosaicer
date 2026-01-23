from PyQt6.QtWidgets import QWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class NoisePlot(QWidget):
    def __init__(self):
        super().__init__()
        self.fig, self.ax = plt.subplots(figsize=(4,3))
        self.canvas = FigureCanvasQTAgg(self.fig)

    def update(self, img):
        self.ax.clear()
        for c, col in enumerate(["R","G","B"]):
            data = img[...,c].flatten()
            self.ax.plot(sorted(data), label=col)
        self.ax.legend()
        self.ax.set_title("Per-channel noise distribution")
        self.canvas.draw()
