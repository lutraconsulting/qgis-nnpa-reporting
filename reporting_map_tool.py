from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis._core import QgsRectangle, QgsGeometry, QgsPoint
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsPointXY, QgsWkbTypes, QgsApplication



class CoordinateCaptureMapTool(QgsMapTool):
    mouseReleased = pyqtSignal(QgsPoint, QgsPoint)
    deactivated = pyqtSignal()


    def __init__(self, canvas):
        super(CoordinateCaptureMapTool, self).__init__(canvas)

        self.mapCanvas = canvas
        self.rubberBand = QgsRubberBand(self.mapCanvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.setCursor(QgsApplication.getThemeCursor(QgsApplication.Cursor.CrossHair))
        self.press_point = None
        self.pressed = False

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.pressed = True
            press_point = QgsPoint(
                self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y())
            )

            self.press_point = press_point

            rect = QgsRectangle(
                self.mapCanvas.getCoordinateTransform().toMapCoordinates(
                    e.x() - 1, e.y() - 1
                ),
                self.mapCanvas.getCoordinateTransform().toMapCoordinates(
                    e.x() + 1, e.y() + 1
                ),
            )
            geom = QgsGeometry().fromRect(rect)
            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
            self.rubberBand.addGeometry(geom)
            self.rubberBand.show()

        elif e.button() == Qt.RightButton:
            pass

    def canvasReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.pressed = False
            release_point = QgsPoint(
                self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y())
            )
            self.mouseReleased.emit(self.press_point, release_point)
        elif e.button() == Qt.RightButton:
            self.deactivate()

    def canvasMoveEvent(self, e):
        if self.pressed:
            move_point = QgsPointXY(
                self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y())
            )

            rect = QgsRectangle(QgsPointXY(self.press_point), move_point)
            geom = QgsGeometry().fromRect(rect)
            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
            self.rubberBand.addGeometry(geom)
            self.rubberBand.show()

    def deactivate(self):
        self.rubberBand.reset(QgsWkbTypes.LineGeometry)
        super(CoordinateCaptureMapTool, self).deactivate()
        self.deactivated.emit()
