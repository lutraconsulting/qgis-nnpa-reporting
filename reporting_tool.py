from PyQt5.QtWidgets import QAction, QMessageBox, QTreeWidgetItem
from PyQt5.uic import loadUiType
from qgis._core import QgsRectangle, QgsFeatureRequest
from qgis.core import QgsPointXY
from .reporting_map_tool import CoordinateCaptureMapTool
from .output_dialog import OutputDialog
from os import path
from PyQt5 import uic

# FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "ui_filter.ui"))


class ReportingTool:
    """QGIS Plugin implementation"""

    def __init__(self, iface):
        self.iface = iface
        self.al = iface.activeLayer()

        self.mapTool = CoordinateCaptureMapTool(self.iface.mapCanvas())
        self.mapTool.mouseReleased.connect(self.mouseReleased)
        self.mapTool.deactivated.connect(self.mtDeactivated)
        # self.mapTool.mousePressed.connect(self.mousePressed)
        self.aoi = None
        # self.setupUI(self)
        self.dialog = OutputDialog()
        self.populate_ranges()

    def initGui(self):
        self.action = QAction("Go!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.dialog.show()

    def mouseReleased(self, point1, point2):
        if point1.x() == point2.x() and point1.y() == point2.y():
            point = self.mapTool.toLayerCoordinatesV2(self.al, point1)
            self.aoi = point.boundingBox()
        else:
            point1 = self.mapTool.toLayerCoordinatesV2(self.al, point1)
            point2 = self.mapTool.toLayerCoordinatesV2(self.al, point2)
            rect = QgsRectangle(QgsPointXY(point1), QgsPointXY(point2))
            self.aoi = rect
        self.build_filter()

    def build_filter(self):
        """Build the filter request"""
        # desired fields
        fields = ["Common_Nam", "Sample_Dat", "Precision"]

        # precision filter
        prec_min = parse_precision(self.dialog.ui.cbPrecisionMin.currentText())
        prec_max = parse_precision(self.dialog.ui.cbPrecisionMax.currentText())
        unique_precision_dict = self.get_unique_precision_values()

        wanted_list_prec = []
        for key, value in unique_precision_dict.items():
            if prec_min <= key <= prec_max:
                wanted_list_prec.append(value)
        wanted_string_prec = "','".join(wanted_list_prec)
        wanted_string_prec = f"('{wanted_string_prec}')"
        precision_filter = f'"Precision" in {wanted_string_prec}'

        # spatial filter
        aoi_buffered = self.aoi.buffered(self.dialog.ui.Buffer.value())

        # exclusion filter
        excluded_names = (
            self.dialog.excluded_names
            if self.dialog.ui.cbExcludeSensitive.isChecked()
            else []
        )
        excluded_names_str = "','".join(excluded_names)
        excluded_names_str = f"('{excluded_names_str}')"
        excluded_names_filter = f'"Common_Nam" not in {excluded_names_str}'

        expression_filter = precision_filter + " and " + excluded_names_filter

        req_filter = (
            QgsFeatureRequest()
            .setFilterRect(aoi_buffered)
            .setFilterExpression(expression_filter)
            # .setFilterExpression(excluded_names_filter)
            .setSubsetOfAttributes(fields, self.al.fields())
        )

        self.format_features(req_filter)

    def format_features(self, req_filter):
        """Format the features that are passing through the filter criteria in the desired format"""
        selected_features = self.al.getFeatures(req_filter)
        output_dict = {}
        for sel_feat in selected_features:
            precision = parse_precision(sel_feat["precision"])
            if sel_feat["Common_Nam"] not in output_dict:
                # the first occurrence
                output_dict[sel_feat["Common_Nam"]] = {
                    "date": sel_feat["Sample_Dat"],
                    "precision_min": precision,
                    "precision_max": precision,
                    "count": 1,
                }
            else:
                # the feature is already in the dict -> increase count and update precision
                dict_feature = output_dict[sel_feat["Common_Nam"]]
                dict_feature["count"] += 1
                if precision > dict_feature["precision_max"]:
                    dict_feature["precision_max"] = precision
                if precision < dict_feature["precision_min"]:
                    dict_feature["precision_min"] = precision

        self.return_result(output_dict)

    def mtDeactivated(self):
        self.dialog.hide()

    def populate_ranges(self):
        """Populate the precision fields in the plugin dialog"""
        unique_precision_dict = self.get_unique_precision_values()
        unique_precision_dict_sorted = dict(sorted(unique_precision_dict.items()))
        self.dialog.ui.cbPrecisionMin.addItems(unique_precision_dict_sorted.values())
        self.dialog.ui.cbPrecisionMax.addItems(unique_precision_dict_sorted.values())

        # set the highest and the lowest values as default
        self.dialog.ui.cbPrecisionMin.setCurrentIndex(0)
        self.dialog.ui.cbPrecisionMax.setCurrentIndex(
            len(unique_precision_dict_sorted) - 1
        )

    def get_unique_precision_values(self):
        """Create dictionary of unique precision values
        {1000: "1km", 10: "10m", etc.}"""
        fields = self.al.fields()
        precision_idx = fields.indexFromName("Precision")
        unique_list = self.al.uniqueValues(precision_idx)
        unique_precision_dict = {}
        for item in unique_list:
            unique_precision_dict[parse_precision(item)] = item
        return unique_precision_dict

    def return_result(self, feature_dict):
        """Display the selected features in the widget"""
        self.dialog.ui.treeResults.clear()

        root_item = self.dialog.ui.treeResults.invisibleRootItem()
        for key, value in feature_dict.items():
            item = QTreeWidgetItem(
                [
                    key,
                    value["date"],
                    str(value["precision_min"]),
                    str(value["precision_max"]),
                    str(value["count"]),
                ]
            )
            root_item.addChild(item)
        self.dialog.ui.treeResults.expandItem(root_item)


def parse_precision(field):
    """Converts to integer in meters
    100m -> 100
    10km -> 10 000
    """
    unit = field.lstrip("0123456789")
    number = field.rstrip(unit)
    meters = int(number) * 1000 if unit == "km" else int(number)
    return meters