# Setting up
- [ ] Build plugin skeleton
- [ ] Clone repo
- [ ] add symlink to qgis plugins
    - linux `ln -s ~/dev/python/qgis-nnpa-reporting/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis-nnpa-reporting`
    - mac `ln -s ~/dev/python/qgis-nnpa-plugin ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-nnpa-plugin`
- [ ] Install the (skeleton) plugin in QGIS
- [ ] Install plugin reloader plugin in QGIS

# Plugin

## 1: Create a map tool
- [ ] tool gets activated when clicking the plugin's button
- [ ] On clicking the map canvas it `print()`s the map's clicked coordinates
### Interesting classes:
`QgsMapCanvas`, `QgsMapTool`

## 2: Differentiate between click and drag
- [ ] Make sure the coordinates are in the same CRS as the layer
- [ ] Print point coords in case of click, rectangle coordinates in case of drag
### Interesting classes/methods:
`QgsVectorLayer`, `QgsMapTool`, `QgsMapTool.canvasPressEvent`, `QgsMapTool.canvasReleaseEvent`

## 3: Interact with the active layer
- [ ] tool queries the active map layer, prints all FIDs intersecting the point / rectangle
### Interesting classes:
`QgisInterface`, `QgsVectorLayer`, `QgsFeatureRequest`

## 4: Display attributes
- [ ] tool requests and prints 3 attributes (name, scale, date)
### Interesting classes:
`QgsFeatureRequest`

## 5: Aggregate data
- [ ] tool aggregates requested data, groups by name, prints name, count, scale range, date range
### Interesting classes:
Python `dict()`

## 6: UI toolbar
- [ ] Add a toolbar for the plugin with 2 buttons: Identify species, settings

## 7: UI input
- [ ] add a dialog with Date range, Scale range, buffer widgets
- [ ] dialog should appear when tool is activated, hide when de-activated
- [ ] Populate the ranges based on actual data (data may need cleanup for this step)
- [ ] Use dialog's values as filters to the `QgsFeatureRequest`
### Interesting classes:
`QComboBox`, `QDateEdit`

## 8: UI output
- [ ] Add a `QTreeWidget` to the dialog, using columns: Species, Count, Date Range, Accuracy Range
- [ ] Populate dialog with tool's results instead of `print()`s
### Interesting classes:
`QTreeWidget`, `QTreeWidgetItem`

## 9: UI settings
TODO
