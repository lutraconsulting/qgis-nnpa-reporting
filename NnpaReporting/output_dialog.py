from os import path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QTreeWidgetItem
from qgis.core import QgsRectangle, QgsFeatureRequest, QgsGeometry, QgsSettings, QgsVectorLayer, Qgis, QgsField, \
    QgsFeature, QgsProject

ui_file = path.join(path.dirname(__file__), "output_dialog.ui")


class OutputDialog(QDialog):
    """Dialog to display the selected features"""

    def __init__(self, layer):
        super().__init__()
        self.ui = uic.loadUi(ui_file, self)
        self.ui.loadAsLayerButton.clicked.connect(self.load_results_as_layer)
        self.layer = layer
        self.geom = None
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
        s = QgsSettings()
        self.excluded_names = s.value('plugins/nnpa_reporting_plugin/sensitive_species', [])
        self.precision_values = []
        self.populate_ranges()

    def populate_ranges(self):
        """Populate the precision fields in the plugin dialog with the unique values"""
        self.precision_values = self.get_unique_precision_values()
        self.cbPrecisionMin.addItems(self.precision_values)
        self.cbPrecisionMax.addItems(self.precision_values)

        # set the highest and the lowest values as default
        self.cbPrecisionMin.setCurrentIndex(0)
        self.cbPrecisionMax.setCurrentIndex(self.cbPrecisionMax.count() - 1)

    def on_mouse_released(self, point1, point2):
        req = self.build_request(point1, point2)
        output_dict = self.perform_request(req)
        self.populate_results(output_dict)

    def build_request(self, point1, point2):
        # precision filter
        prec_min = min(self.cbPrecisionMin.currentIndex(), self.cbPrecisionMax.currentIndex())
        prec_max = max(self.cbPrecisionMin.currentIndex(), self.cbPrecisionMax.currentIndex())

        wanted_list_prec = []
        for i in range(prec_min, prec_max + 1):
            wanted_list_prec.append(self.precision_values[i])

        wanted_string_prec = f"""'{"','".join(wanted_list_prec)}'"""
        precision_filter = f'"Precision" in ({wanted_string_prec})'

        # buffer
        self.buffer_value = self.qgsDoubleSpinBoxBuffer.value()
        if point1 == point2:
            self.geom = QgsGeometry.fromPointXY(point1)
        else:
            self.geom = QgsGeometry.fromRect(QgsRectangle(point1, point2))

        # exclusion filter
        excluded_names = (
            self.excluded_names if self.cbExcludeSensitive.isChecked() else []
        )
        expression_filter = precision_filter
        if excluded_names:
            excluded_names_str = f"""'{"','".join(excluded_names)}'"""
            excluded_names_filter = f'"Common_Nam" not in ({excluded_names_str})'
            expression_filter += f" and {excluded_names_filter}"

        # desired fields
        fields = ["Common_Nam", "Sample_Dat", "Precision"]

        return (QgsFeatureRequest()
                .setDistanceWithin(self.geom, self.buffer_value)
                .setFilterExpression(expression_filter)
                .setFlags(QgsFeatureRequest.NoGeometry)
                .setFlags(QgsFeatureRequest.ExactIntersect)
                .setSubsetOfAttributes(fields, self.layer.fields())
                )

    def perform_request(self, req):
        """Format the features that are passing through the filter to the desired format"""
        output_dict = {}
        for sel_feat in self.layer.getFeatures(req):
            if sel_feat["Common_Nam"] not in output_dict:
                # the first occurrence
                output_dict[sel_feat["Common_Nam"]] = {
                    "date": [sel_feat["Sample_Dat"]],
                    "precision_min": sel_feat["precision"],
                    "precision_max": sel_feat["precision"],
                    "count": 1,
                }
            else:
                # the feature is already in the dict -> increase count, update date and precision fields
                dict_feature = output_dict[sel_feat["Common_Nam"]]

                dict_feature["count"] += 1
                dict_feature["date"].append(sel_feat["Sample_Dat"])

                if self.precision_values.index(sel_feat["precision"]) > self.precision_values.index(dict_feature["precision_max"]):
                    dict_feature["precision_max"] = sel_feat["precision"]

                if self.precision_values.index(sel_feat["precision"]) < self.precision_values.index(dict_feature["precision_min"]):
                    dict_feature["precision_min"] = sel_feat["precision"]

        return output_dict

    def populate_results(self, feature_dict):
        """Display the selected features in the tree widget"""
        self.treeResults.clear()

        root_item = self.treeResults.invisibleRootItem()
        for key, value in feature_dict.items():
            item = TreeWidgetItem(
                [
                    key,
                    str(value["count"]),
                    ", ".join(set(value["date"])),
                    value["precision_min"],
                    value["precision_max"],
                ]
            )
            root_item.addChild(item)

        total_count = sum(item["count"] for item in feature_dict.values())
        self.treeResults.expandItem(root_item)
        self.lbTotal.setText(f"Total: {total_count}")
        self.show_and_activate()

    def get_unique_precision_values(self):
        """Return a sorted list of unique precision values from the layer
        ['100m', '1km', '10km', etc.]"""
        fields = self.layer.fields()
        precision_idx = fields.indexFromName("Precision")
        unique_list = self.layer.uniqueValues(precision_idx)

        precision_dict = {}
        for value in unique_list:
            unit = value.lstrip("0123456789")
            number = value.rstrip(unit)
            meters = int(number) * 1000 if unit == "km" else int(number)
            precision_dict[meters] = value

        return [v[1] for v in sorted(precision_dict.items())]

    def show_and_activate(self):
        self.show()
        self.activateWindow()

    def load_results_as_layer(self):
        root_item = self.treeResults.invisibleRootItem()
        if root_item.childCount() == 0:
            return

        if self.buffer_value:
            geom = self.geom.buffer(self.buffer_value, 20)
        else:
            geom = self.geom

        if geom.type() == Qgis.GeometryType.Point:
            vl = QgsVectorLayer("Point", "query_results", "memory")
        else:
            vl = QgsVectorLayer("Polygon", "query_results", "memory")

        vl.setCrs(self.layer.crs())
        dp = vl.dataProvider()
        dp.addAttributes([QgsField("Common Name", QVariant.String),
                          QgsField("Count", QVariant.Int),
                          QgsField("Observation Date", QVariant.String),
                          QgsField("Precision Min", QVariant.String),
                          QgsField("Precision Max", QVariant.String),
                          ])
        vl.updateFields()

        root_item = self.treeResults.invisibleRootItem()
        for i in range(root_item.childCount()):
            item = root_item.child(i)
            f = QgsFeature(dp.fields())
            f.setAttributes([item.text(0),
                             item.text(1),
                             item.text(2),
                             item.text(3),
                             item.text(4)])
            f.setGeometry(geom)
            dp.addFeature(f)

        QgsProject.instance().addMapLayer(vl)


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
