from qgis.PyQt.QtWidgets import QAction, QDialog
from qgis.core import QgsSettings, QgsVectorLayer

from .settings_dialog import SettingsDialog
from .reporting_map_tool import ReportingMapTool


class ReportingTool:
    """QGIS Plugin implementation"""

    def __init__(self, iface):
        self.iface = iface
        self.layer = None
        self.mapTool = None
        s = QgsSettings()
        layerUri = s.value('plugins/nnpa_reporting_plugin/layer_uri', None)
        layerProvider = s.value('plugins/nnpa_reporting_plugin/layer_provider', None)
        if layerUri and layerProvider:
            self.setLayer(layerUri, layerProvider)

    def setLayer(self, uri, provider):
        self.layer = QgsVectorLayer(uri, "nnpa_reporting_layer", provider)
        self.mapTool = ReportingMapTool(self.iface, self.layer)

    def initGui(self):
        action = QAction("Reporting tool", self.iface.mainWindow())
        action.triggered.connect(self.run)
        settingsAction = QAction("Settings", self.iface.mainWindow())
        settingsAction.triggered.connect(self.openSettings)
        self.toolBar = self.iface.addToolBar('NNPA Reporting Tool')
        self.toolBar.setToolTip("NNPA Reporting Toolbar")
        self.toolBar.setObjectName("NNPAReportingToolbar")
        self.toolBar.addAction(action)
        self.toolBar.addAction(settingsAction)

    def unload(self):
        self.mapTool.deleteLater()
        self.toolBar.deleteLater()
        del self.toolBar

    def run(self):
        s = QgsSettings()
        name_field_name = s.value('plugins/nnpa_reporting_plugin/name_field_name', "Common_nam")
        date_field_name = s.value('plugins/nnpa_reporting_plugin/date_field_name', "Sample_dat")
        precision_field_name = s.value('plugins/nnpa_reporting_plugin/precision_field_name', "Precision")
        if not self.layer or \
                not self.layer.isValid() or \
                self.layer.fields().indexOf(name_field_name) < 0 or \
                self.layer.fields().indexOf(date_field_name) < 0 or \
                self.layer.fields().indexOf(precision_field_name) < 0:
            self.openSettings()
            return
        self.iface.mapCanvas().setMapTool(self.mapTool)

    def openSettings(self):
        dlg = SettingsDialog(self.iface)
        if dlg.exec() == QDialog.Accepted:
            self.setLayer(dlg.layer_uri, dlg.layer_provider)
