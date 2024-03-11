import csv
from os import path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QFileDialog, QTreeWidgetItem
from qgis.core import QgsRectangle, QgsFeatureRequest, QgsPointXY, QgsGeometry

ui_file = path.join(path.dirname(__file__), "ui_filter.ui")


class OutputDialog(QDialog):
    """Dialog to display the selected features"""

    show_dialog = pyqtSignal()

    def __init__(self, active_layer, mapTool):
        super().__init__()
        self.ui = uic.loadUi(ui_file, self)
        self.al = active_layer
        self.treeResults.setHeaderLabels(
            [
                "Common Name",
                "Count",
                "Observation Date",
                "Precision Min",
                "Precision Max",
            ]
        )
        self.treeResults.header().resizeSections(QHeaderView.ResizeToContents)
        self.btLoadCsv.clicked.connect(self.load_csv)
        self.excluded_names = []
        self.populate_ranges()
        self.mapTool = mapTool
        self.mapTool.mouseReleased.connect(self.on_mouse_released)

    def on_mouse_released(self, point1, point2):
        point1 = self.mapTool.toLayerCoordinatesV2(self.al, point1)
        point2 = self.mapTool.toLayerCoordinatesV2(self.al, point2)
        if point1 == point2:
            aoi = QgsRectangle(
                point1.x() - 1, point1.y() - 1, point1.x() + 1, point1.y() + 1
            )
        else:
            aoi = QgsRectangle(QgsPointXY(point1), QgsPointXY(point2))
        self.build_filter(aoi)

    def build_filter(self, aoi):
        """Build the filter request"""
        # desired fields
        fields = ["Common_Nam", "Sample_Dat", "Precision"]

        # precision filter
        prec_min = list(precision_str_to_dict([self.cbPrecisionMin.currentText()]))[0]
        prec_max = list(precision_str_to_dict([self.cbPrecisionMax.currentText()]))[0]
        unique_precision_dict = self.get_unique_precision_values()

        wanted_list_prec = []
        for key, value in unique_precision_dict.items():
            if prec_min <= key <= prec_max:
                wanted_list_prec.append(value)
        wanted_string_prec = "'" + "','".join(wanted_list_prec) + "'"
        precision_filter = f'"Precision" in ({wanted_string_prec})'

        # buffer
        buffer_value = self.qgsDoubleSpinBoxBuffer.value()
        rect = QgsGeometry.fromRect(aoi)

        # exclusion filter
        excluded_names = (
            self.excluded_names if self.cbExcludeSensitive.isChecked() else []
        )
        excluded_names_str = "'" + "','".join(excluded_names) + "'"
        excluded_names_filter = f'"Common_Nam" not in ({excluded_names_str})'

        expression_filter = precision_filter + " and " + excluded_names_filter

        req_filter = (
            QgsFeatureRequest()
            .setDistanceWithin(rect, buffer_value)
            .setFilterExpression(expression_filter)
            .setFlags(QgsFeatureRequest.NoGeometry)
            .setFlags(QgsFeatureRequest.ExactIntersect)
            .setSubsetOfAttributes(fields, self.al.fields())
        )

        self.format_features(req_filter)

    def format_features(self, req_filter):
        """Format the features that are passing through the filter to the desired format"""
        output_dict = {}
        for sel_feat in self.al.getFeatures(req_filter):
            precision_dict = precision_str_to_dict([sel_feat["precision"]])
            if sel_feat["Common_Nam"] not in output_dict:
                # the first occurrence
                output_dict[sel_feat["Common_Nam"]] = {
                    "date": [sel_feat["Sample_Dat"]],
                    "precision_min": precision_dict,
                    "precision_max": precision_dict,
                    "count": 1,
                }
            else:
                # the feature is already in the dict -> increase count, update date and precision fields
                dict_feature = output_dict[sel_feat["Common_Nam"]]

                dict_feature["count"] += 1
                dict_feature["date"].append(sel_feat["Sample_Dat"])

                highest_key = max(
                    dict_feature["precision_max"].keys() | precision_dict.keys()
                )
                lowest_key = min(
                    dict_feature["precision_min"].keys() | precision_dict.keys()
                )
                if highest_key in precision_dict:
                    dict_feature["precision_max"] = precision_dict
                elif lowest_key in precision_dict:
                    dict_feature["precision_min"] = precision_dict

        self.return_result(output_dict)

    def return_result(self, feature_dict):
        """Display the selected features in the tree widget"""
        self.treeResults.clear()

        root_item = self.treeResults.invisibleRootItem()
        for key, value in feature_dict.items():
            item = TreeWidgetItem(
                [
                    key,
                    str(value["count"]),
                    ", ".join(set(value["date"])),
                    list(value["precision_min"].values())[0],
                    list(value["precision_max"].values())[0],
                ]
            )
            root_item.addChild(item)

        total_count = sum(item["count"] for item in feature_dict.values())
        self.treeResults.expandItem(root_item)
        self.lbTotal.setText(f"Total: {total_count}")
        self.show()

    def populate_ranges(self):
        """Populate the precision fields in the plugin dialog with the unique values"""
        unique_precision_dict = self.get_unique_precision_values()
        unique_precision_dict_sorted = dict(sorted(unique_precision_dict.items()))
        self.cbPrecisionMin.addItems(unique_precision_dict_sorted.values())
        self.cbPrecisionMax.addItems(unique_precision_dict_sorted.values())

        # set the highest and the lowest values as default
        self.cbPrecisionMin.setCurrentIndex(0)
        self.cbPrecisionMax.setCurrentIndex(len(unique_precision_dict_sorted) - 1)

    def get_unique_precision_values(self):
        """Create dictionary of unique precision values from the active layer
        {1000: "1km", 10: "10m", etc.}"""
        fields = self.al.fields()
        precision_idx = fields.indexFromName("Precision")
        unique_list = self.al.uniqueValues(precision_idx)
        return precision_str_to_dict(unique_list)

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
            self.cbExcludeSensitive.setChecked(True)
            self.btLoadCsv.setText(path.basename(file_name))


class TreeWidgetItem(QTreeWidgetItem):
    """Custom class to enable sorting 'Count' column - integers converted to string"""
    def __init__(self, parent=None):
        QTreeWidgetItem.__init__(self, parent)

    def __lt__(self, other_item):
        column = self.treeWidget().sortColumn()
        try:
            return float(self.text(column)) > float(other_item.text(column))
        except ValueError:
            return self.text(column) > other_item.text(column)


def precision_str_to_dict(fields: list) -> dict:
    """Converts to dictionary with integer key in meters
    ['100m', '10km'] -> {100: '100m', 10 000: '10km'}
    """

    precision_dict = {}
    for field in fields:
        unit = field.lstrip("0123456789")
        number = field.rstrip(unit)
        meters = int(number) * 1000 if unit == "km" else int(number)
        precision_dict[meters] = field
    return precision_dict
