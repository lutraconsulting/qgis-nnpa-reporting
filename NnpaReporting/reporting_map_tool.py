from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsIdentifyMenu
from qgis.core import (
    Qgis,
    QgsRectangle,
    QgsGeometry,
    QgsApplication,
    QgsCoordinateTransform,
    QgsCsException,
    QgsProject
)
from qgis.gui import QgsMapTool, QgsRubberBand

from .output_dialog import OutputDialog


class ReportingMapTool(QgsMapTool):
    """A class fot handling map tool mouse events"""

    def __init__(self, iface, layer):
        super(ReportingMapTool, self).__init__(iface.mapCanvas())

        self.iface = iface
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
        if e.button() == Qt.RightButton:
            self.pressed = False
            self.rubberBand.reset()
            self.dialog.treeResults.clear()

        if e.button() != Qt.LeftButton:
            return

        if self.dialog.cbMode.currentData() == 0:
            if self.pressed:
                point1 = self.toLayerCoordinates(self.layer, self.press_point)
                point2 = self.toLayerCoordinates(self.layer, e.mapPoint())
                if point1 == point2:
                    geom = QgsGeometry.fromPointXY(point1)
                else:
                    geom = QgsGeometry.fromRect(QgsRectangle(point1, point2))
                self.dialog.on_mouse_released(geom)

        elif self.dialog.cbMode.currentData() == 1:
            pass
        elif self.dialog.cbMode.currentData() == 2:
            identifyMenu = QgsIdentifyMenu(self.canvas())
            identifyMenu.setAllowMultipleReturn(False)
            identifyMenu.setExecWithSingleResult(True)
            results = QgsIdentifyMenu.findFeaturesOnCanvas(e, self.canvas(), [Qgis.GeometryType.Polygon])
            globalPos = self.canvas().mapToGlobal(QPoint(e.pos().x() + 5, e.pos().y() + 5))
            selectedFeatures = identifyMenu.exec(results, globalPos)
            if selectedFeatures and selectedFeatures[0].mFeature.hasGeometry():
                transform = QgsCoordinateTransform(selectedFeatures[0].mLayer.crs(), self.layer.crs(), QgsProject.instance())
                geom = selectedFeatures[0].mFeature.geometry()
                try:
                    geom.transform(transform)
                except QgsCsException:
                    pass

                self.dialog.on_mouse_released(geom)

        self.pressed = False

    def canvasMoveEvent(self, e):
        if self.pressed:
            self.rubberBand.setToGeometry(QgsGeometry.fromRect(QgsRectangle(self.press_point, e.mapPoint())))
            self.rubberBand.show()
