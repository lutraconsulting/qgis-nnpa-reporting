from os import path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsSettings, QgsFields

ui_file = path.join(path.dirname(__file__), "fields_dialog.ui")


class FieldsDialog(QDialog):
    def __init__(self, parent, fields: QgsFields):
        super().__init__(parent)
        self.ui = uic.loadUi(ui_file, self)

        for field in fields:
            if field.type() != QVariant.String:
                continue
            self.ui.nameComboBox.addItem(field.name())
            self.ui.dateComboBox.addItem(field.name())
            self.ui.precisionComboBox.addItem(field.name())

        self.ui.nameComboBox.setCurrentIndex(-1)
        self.ui.dateComboBox.setCurrentIndex(-1)
        self.ui.precisionComboBox.setCurrentIndex(-1)

        s = QgsSettings()
        nameFieldName = s.value('plugins/nnpa_reporting_plugin/name_field_name', "Common_Nam")
        dateFieldName = s.value('plugins/nnpa_reporting_plugin/date_field_name', "Sample_Dat")
        precisionFieldName = s.value('plugins/nnpa_reporting_plugin/precision_field_name', "Precision")

        self.ui.nameComboBox.setCurrentText(nameFieldName)
        self.ui.dateComboBox.setCurrentText(dateFieldName)
        self.ui.precisionComboBox.setCurrentText(precisionFieldName)

    def accept(self):
        if self.ui.nameComboBox.currentIndex() < 0 or \
                self.ui.dateComboBox.currentIndex() < 0 or \
                self.ui.precisionComboBox.currentIndex() < 0:
            return

        nameFieldName = self.ui.nameComboBox.currentText()
        dateFieldName = self.ui.dateComboBox.currentText()
        precisionFieldName = self.ui.precisionComboBox.currentText()
        s = QgsSettings()
        s.setValue('plugins/nnpa_reporting_plugin/name_field_name', nameFieldName)
        s.setValue('plugins/nnpa_reporting_plugin/date_field_name', dateFieldName)
        s.setValue('plugins/nnpa_reporting_plugin/precision_field_name', precisionFieldName)
        super().accept()
