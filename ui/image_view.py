from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QPainter


class ImageView(QGraphicsView):
    pixelHovered = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Scene setup ---
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # --- Pixmap item (created ONCE) ---
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # --- Stored references ---
        self._qimage = None
        self._pixmap = None

        # --- Interaction state ---
        self._panning = False
        self._pan_start = QPoint()

        # --- View config ---
        self.setMouseTracking(True)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

    # ------------------------------------------------------------
    # Image handling
    # ------------------------------------------------------------

    # Display a new image (Qt-owned QImage)
    def setImage(self, qimage):

        self._qimage = qimage
        self._pixmap = QPixmap.fromImage(qimage)

        self.pixmap_item.setPixmap(self._pixmap)
        self.scene.setSceneRect(self._pixmap.rect().toRectF())

        # Fit image on load
        self.resetTransform()
        self.fitInView(
            self.scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )

    # ------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------

    # Zoom with mouse wheel
    def wheelEvent(self, event):

        if self._pixmap is None:
            return

        zoom_in = 1.25
        zoom_out = 1 / zoom_in

        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        if self._panning:

            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            return

        if self._pixmap is None:
            return

        scene_pos = self.mapToScene(event.pos())
        item_pos = self.pixmap_item.mapFromScene(scene_pos)

        x = int(item_pos.x())
        y = int(item_pos.y())

        if (
            0 <= x < self._pixmap.width()
            and 0 <= y < self._pixmap.height()
        ):
            self.pixelHovered.emit(x, y)

            super().mouseMoveEvent(event)

    # Reset zoom to 100%
    def zoom_100(self):

        self.resetTransform()

    # Fit image to view
    def fitToView(self):

        if self._pixmap:
            self.resetTransform()
            self.fitInView(
                self.scene.sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
