from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsRectangle,
    QgsGeometry,
    QgsApplication,
)
from qgis.gui import QgsMapTool, QgsRubberBand

from .output_dialog import OutputDialog


class ReportingMapTool(QgsMapTool):
    """A class fot handling map tool mouse events"""

    def __init__(self, canvas, layer):
        super(ReportingMapTool, self).__init__(canvas)

        self.layer = layer
        self.dialog = OutputDialog(self.layer)
        self.rubberBand = QgsRubberBand(self.canvas())
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setFillColor(QColor(255, 0, 0, 127))  # semi-transparent red
        self.rubberBand.setWidth(1)
        self.setCursor(QgsApplication.getThemeCursor(QgsApplication.Cursor.CrossHair))
        self.press_point = None
        self.pressed = False

        self.activated.connect(self.dialog.show_and_activate)
        self.reactivated.connect(self.dialog.show_and_activate)
        self.deactivated.connect(self.rubberBand.reset)

    def __del__(self):
        self.dialog.deleteLater()

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.pressed = True
            self.press_point = e.mapPoint()
            self.rubberBand.setToGeometry(QgsGeometry.fromPointXY(e.mapPoint()))
            self.rubberBand.show()

    def canvasReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.pressed:
            point1 = self.toLayerCoordinates(self.layer, self.press_point)
            point2 = self.toLayerCoordinates(self.layer, e.mapPoint())
            self.dialog.on_mouse_released(point1, point2)
        elif e.button() == Qt.RightButton:
            self.rubberBand.reset()
            self.dialog.treeResults.clear()
        self.pressed = False

    def canvasMoveEvent(self, e):
        if self.pressed:
            self.rubberBand.setToGeometry(QgsGeometry.fromRect(QgsRectangle(self.press_point, e.mapPoint())))
            self.rubberBand.show()
