import csv
from os import path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QFileDialog, QTreeWidgetItem

ui_file = path.join(path.dirname(__file__), "ui_filter.ui")


class OutputDialog(QDialog):
    """Dialog to display the selected features"""

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(ui_file, self)
        self.ui.treeResults.setHeaderLabels(
            [
                "Common Name",
                "Count",
                "Observation Date",
                "Precision Min",
                "Precision Max",
            ]
        )
        self.ui.treeResults.header().resizeSections(QHeaderView.ResizeToContents)
        self.ui.loadCsv.clicked.connect(self.load_csv)
        self.excluded_names = []

    def load_csv(self):
        """Loads CSV file and adds items to the exclusion list"""
        (file_name, _) = QFileDialog.getOpenFileName(
            self, "Load CSV exclusion list", "~", "CSV Files (*.csv)"
        )

        if file_name:
            with open(file_name, "r") as input_csv:
                reader = csv.DictReader(input_csv)
                for row in reader:
                    self.excluded_names.append(row["Common Name"])


class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent=None):
        QTreeWidgetItem.__init__(self, parent)

    def __lt__(self, other_item):
        column = self.treeWidget().sortColumn()
        try:
            return float(self.text(column)) > float(other_item.text(column))
        except ValueError:
            return self.text(column) > other_item.text(column)
