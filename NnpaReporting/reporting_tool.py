from qgis.core import QgsSettings, QgsVectorLayer
from qgis.PyQt.QtWidgets import QAction, QDialog

from .reporting_map_tool import ReportingMapTool
from .settings_dialog import SettingsDialog


class ReportingTool:
    """QGIS Plugin implementation"""

    def __init__(self, iface):
        self.iface = iface
        self.layer = None
        self.mapTool = None
        s = QgsSettings()
        layer_uri = s.value("plugins/nnpa_reporting_plugin/layer_uri", None)
        layer_provider = s.value("plugins/nnpa_reporting_plugin/layer_provider", None)
        if layer_uri and layer_provider:
            self.setLayer(layer_uri, layer_provider)

    def setLayer(self, uri, provider):
        self.layer = QgsVectorLayer(uri, "nnpa_reporting_layer", provider)
        self.mapTool = ReportingMapTool(self.iface, self.layer)

    def initGui(self):
        action = QAction("Reporting tool", self.iface.mainWindow())
        action.triggered.connect(self.run)
        settingsAction = QAction("Settings", self.iface.mainWindow())
        settingsAction.triggered.connect(self.openSettings)
        self.toolBar = self.iface.addToolBar("NNPA Reporting Tool")
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
        name_field_name = s.value("plugins/nnpa_reporting_plugin/name_field_name", "Common_nam")
        date_field_name = s.value("plugins/nnpa_reporting_plugin/date_field_name", "Sample_dat")
        precision_field_name = s.value("plugins/nnpa_reporting_plugin/precision_field_name", "Precision")
        grid_refer_field_name = s.value("plugins/nnpa_reporting_plugin/grid_refer_field_name", "grid refer")
        latin_name_field_name = s.value("plugins/nnpa_reporting_plugin/latin_name_field_name", "latin name")
        recorder_field_name = s.value("plugins/nnpa_reporting_plugin/recorder_field_name", "recorder")
        survey_field_name = s.value("plugins/nnpa_reporting_plugin/survey_field_name", "survey nam")
        field_names = [
            name_field_name,
            date_field_name,
            precision_field_name,
            grid_refer_field_name,
            latin_name_field_name,
            recorder_field_name,
            survey_field_name,
        ]
        if (
            not self.layer
            or not self.layer.isValid()
            or any(self.layer.fields().indexOf(field_name) < 0 for field_name in field_names)
        ):
            self.openSettings()
            return
        self.iface.mapCanvas().setMapTool(self.mapTool)

    def openSettings(self):
        dlg = SettingsDialog(self.iface)
        if dlg.exec() == QDialog.Accepted:
            self.setLayer(dlg.layer_uri, dlg.layer_provider)
