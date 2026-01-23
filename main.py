import sys
from PyQt6.QtWidgets import QApplication, QFileDialog
from pipeline.raw_context import RawContext
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    path, _ = QFileDialog.getOpenFileName(
        None,
        "Open RAW file",
        "",
        "RAW files (*.CR3 *.cr3 *.CR2 *.NEF *.ARW)"
    )

    if not path:
        sys.exit(0)

    ctx = RawContext(path)
    win = MainWindow(ctx)
    win.resize(1400, 900)
    win.show()

    sys.exit(app.exec())
