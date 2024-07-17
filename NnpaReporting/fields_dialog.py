from os import path

from qgis.core import QgsFields, QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog

ui_file = path.join(path.dirname(__file__), "fields_dialog.ui")


class FieldsDialog(QDialog):
    def __init__(self, parent, fields: QgsFields):
        super().__init__(parent)
        self.ui = uic.loadUi(ui_file, self)

        for field in fields:
            if field.type() != QVariant.String:
                continue
            for field_combo_box in self.field_selection_widgets:
                field_combo_box.addItem(field.name())
        for field_combo_box in self.field_selection_widgets:
            field_combo_box.setCurrentIndex(-1)

        s = QgsSettings()
        name_field_name = s.value("plugins/nnpa_reporting_plugin/name_field_name", "Common_Nam")
        date_field_name = s.value("plugins/nnpa_reporting_plugin/date_field_name", "Sample_Dat")
        precision_field_name = s.value("plugins/nnpa_reporting_plugin/precision_field_name", "Precision")
        grid_refer_field_name = s.value("plugins/nnpa_reporting_plugin/grid_refer_field_name", "grid refer")
        latin_name_field_name = s.value("plugins/nnpa_reporting_plugin/latin_name_field_name", "latin name")
        recorder_field_name = s.value("plugins/nnpa_reporting_plugin/recorder_field_name", "recorder")
        survey_field_name = s.value("plugins/nnpa_reporting_plugin/survey_field_name", "survey nam")

        self.ui.name_cbo.setCurrentText(name_field_name)
        self.ui.date_cbo.setCurrentText(date_field_name)
        self.ui.precision_cbo.setCurrentText(precision_field_name)
        self.ui.grid_refer_cbo.setCurrentText(grid_refer_field_name)
        self.ui.latin_name_cbo.setCurrentText(latin_name_field_name)
        self.ui.recorder_cbo.setCurrentText(recorder_field_name)
        self.ui.survey_cbo.setCurrentText(survey_field_name)

    @property
    def field_selection_widgets(self):
        field_combo_boxes = [
            self.ui.name_cbo,
            self.ui.date_cbo,
            self.ui.precision_cbo,
            self.ui.grid_refer_cbo,
            self.ui.latin_name_cbo,
            self.ui.recorder_cbo,
            self.ui.survey_cbo,
        ]
        return field_combo_boxes

    def accept(self):
        if any(combo_box.currentIndex() < 0 for combo_box in self.field_selection_widgets):
            return

        name_field_name = self.ui.name_cbo.currentText()
        date_field_name = self.ui.date_cbo.currentText()
        precision_field_name = self.ui.precision_cbo.currentText()
        grid_refer_field_name = self.ui.grid_refer_cbo.currentText()
        latin_name_field_name = self.ui.latin_name_cbo.currentText()
        recorder_field_name = self.ui.recorder_cbo.currentText()
        survey_field_name = self.ui.survey_cbo.currentText()
        s = QgsSettings()
        s.setValue("plugins/nnpa_reporting_plugin/name_field_name", name_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/date_field_name", date_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/precision_field_name", precision_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/grid_refer_field_name", grid_refer_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/latin_name_field_name", latin_name_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/recorder_field_name", recorder_field_name)
        s.setValue("plugins/nnpa_reporting_plugin/survey_field_name", survey_field_name)
        super().accept()
