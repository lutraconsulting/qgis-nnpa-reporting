import csv
from os import path

from qgis.core import Qgis, QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox

from .fields_dialog import FieldsDialog

ui_file = path.join(path.dirname(__file__), "settings_dialog.ui")


class SettingsDialog(QDialog):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.ui = uic.loadUi(ui_file, self)

        self.iface = iface

        self.ui.layerComboBox.setFilters(Qgis.LayerFilter.PolygonLayer)
        self.ui.setFromLayerButton.clicked.connect(self.on_pick_layer)
        self.ui.loadCsvButton.clicked.connect(self.load_csv)

        s = QgsSettings()
        self.layer_uri = s.value("plugins/nnpa_reporting_plugin/layer_uri", None)
        self.layer_provider = s.value("plugins/nnpa_reporting_plugin/layer_provider", None)
        self.ui.uriLineEdit.setText(self.layer_uri)
        self.sensitive_species = s.value("plugins/nnpa_reporting_plugin/sensitive_species", [])
        self.ui.sensitiveSpeciesTextEdit.setPlainText("\n".join(self.sensitive_species))

    def on_pick_layer(self):
        layer = self.ui.layerComboBox.currentLayer()
        if not layer or not layer.isValid():
            return

        dlg = FieldsDialog(self, layer.fields())
        if dlg.exec() == QDialog.Accepted:
            self.layer_uri = layer.dataProvider().dataSourceUri(True)
            self.layer_provider = layer.dataProvider().name()
            self.ui.uriLineEdit.setText(self.layer_uri)

    def accept(self):
        self.save_settings()
        super().accept()

    def save_settings(self):
        s = QgsSettings()
        s.setValue("plugins/nnpa_reporting_plugin/layer_uri", self.layer_uri)
        s.setValue("plugins/nnpa_reporting_plugin/layer_provider", self.layer_provider)
        s.setValue("plugins/nnpa_reporting_plugin/sensitive_species", self.sensitive_species)

    def load_csv(self):
        """Loads CSV file and adds items to the exclusion list"""
        (file_name, _) = QFileDialog.getOpenFileName(self, "Load CSV exclusion list", "~", "CSV Files (*.csv)")

        if file_name:
            with open(file_name, "r") as input_csv:
                species = []
                reader = csv.DictReader(input_csv)
                try:
                    for row in reader:
                        species.append(row["Common Name"])
                    self.sensitive_species = species
                except KeyError:
                    QMessageBox.critical(self, "Error", "Field 'Common Name' was not found in the selected file")
                    return

                self.ui.sensitiveSpeciesTextEdit.setPlainText("\n".join(self.sensitive_species))
