from qgis.PyQt.QtWidgets import QAction

from .reporting_map_tool import CoordinateCaptureMapTool
from .output_dialog import OutputDialog


class ReportingTool:
    """QGIS Plugin implementation"""

    def __init__(self, iface):
        self.iface = iface
        self.al = iface.activeLayer()
        self.mapTool = CoordinateCaptureMapTool(self.iface.mapCanvas())
        self.dialog = OutputDialog(self.al, self.mapTool)
        self.mapTool.deactivated.connect(self.dialog.hide)
        self.dialog.show_dialog.connect(self.on_show_dialog)

    def initGui(self):
        self.action = QAction("Reporting tool", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.dialog.show()

    def on_show_dialog(self):
        self.dialog.show()
