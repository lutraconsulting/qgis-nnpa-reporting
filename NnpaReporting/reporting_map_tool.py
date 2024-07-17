from qgis.core import Qgis, QgsApplication, QgsCsException, QgsGeometry, QgsRectangle
from qgis.gui import QgsIdentifyMenu, QgsMapTool, QgsRubberBand
from qgis.PyQt.QtCore import QPoint, Qt
from qgis.PyQt.QtGui import QColor

from .output_dialog import IdentifyMode, OutputDialog


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
        self.digitizing_polygon = False

        self.activated.connect(self.dialog.show_and_activate)
        self.reactivated.connect(self.dialog.show_and_activate)
        self.deactivated.connect(self.rubberBand.reset)

    def __del__(self):
        self.dialog.deleteLater()

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.dialog.cbMode.currentData() == IdentifyMode.POINT:
                self.pressed = True
                self.press_point = e.mapPoint()
                self.rubberBand.setToGeometry(QgsGeometry.fromPointXY(e.mapPoint()))
                self.rubberBand.show()
            elif self.dialog.cbMode.currentData() == IdentifyMode.POLYGON:
                if not self.digitizing_polygon:
                    self.rubberBand.reset(Qgis.GeometryType.Polygon)
                self.digitizing_polygon = True
                self.rubberBand.show()

    def canvasReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            if self.dialog.cbMode.currentData() == IdentifyMode.POLYGON and self.digitizing_polygon:
                self.rubberBand.removeLastPoint()
                self.finishDigitizing()
            else:
                self.resetDigitizing()

        if e.button() != Qt.LeftButton:
            return

        if self.dialog.cbMode.currentData() == IdentifyMode.POINT:
            if self.pressed:
                self.finishDigitizing()

        elif self.dialog.cbMode.currentData() == IdentifyMode.POLYGON:
            self.rubberBand.addPoint(e.mapPoint())
        elif self.dialog.cbMode.currentData() == IdentifyMode.LAYER:
            self.rubberBand.reset()
            identifyMenu = QgsIdentifyMenu(self.canvas())
            identifyMenu.setAllowMultipleReturn(False)
            identifyMenu.setExecWithSingleResult(True)
            results = QgsIdentifyMenu.findFeaturesOnCanvas(e, self.canvas(), [Qgis.GeometryType.Polygon])
            # remove results from our own layer
            results = [
                r
                for r in results
                if r.mLayer.dataProvider().dataSourceUri() != self.layer.dataProvider().dataSourceUri()
            ]
            globalPos = self.canvas().mapToGlobal(QPoint(e.pos().x() + 5, e.pos().y() + 5))
            selectedFeatures = identifyMenu.exec(results, globalPos)
            if selectedFeatures and selectedFeatures[0].mFeature.hasGeometry():
                geom = selectedFeatures[0].mFeature.geometry()
                transform = self.canvas().mapSettings().layerTransform(selectedFeatures[0].mLayer)
                try:
                    geom.transform(transform)
                except QgsCsException:
                    pass

                self.rubberBand.setToGeometry(geom)
                self.finishDigitizing()

    def canvasMoveEvent(self, e):
        if self.dialog.cbMode.currentData() == IdentifyMode.POINT and self.pressed:
            self.rubberBand.setToGeometry(QgsGeometry.fromRect(QgsRectangle(self.press_point, e.mapPoint())))
            self.rubberBand.show()
        elif self.dialog.cbMode.currentData() == IdentifyMode.POLYGON and self.digitizing_polygon:
            self.rubberBand.movePoint(e.mapPoint())
            self.rubberBand.show()

    def finishDigitizing(self):
        transform = self.canvas().mapSettings().layerTransform(self.layer)
        geom = self.rubberBand.asGeometry()
        try:
            geom.transform(transform, Qgis.TransformDirection.ReverseTransform)
        except QgsCsException:
            pass

        self.dialog.search_using_geometry(geom)
        self.pressed = False
        self.digitizing_polygon = False

    def resetDigitizing(self):
        self.pressed = False
        self.digitizing_polygon = False
        self.rubberBand.reset()
        self.dialog.clearResults()
