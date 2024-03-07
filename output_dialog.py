import csv
from os import path

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QHeaderView, QFileDialog

ui_file = path.join(path.dirname(__file__), "ui_filter.ui")


class OutputDialog(QDialog):
    """Dialog to display the selected features"""
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(ui_file, self)
        self.ui.treeResults.setHeaderLabels(
            [
                "Common Name",
                "Observation Date",
                "Precision Min [m]",
                "Precision Max [m]",
                "Count",
            ]
        )
        self.ui.treeResults.header().setSectionResizeMode(QHeaderView.ResizeToContents)
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

