import json
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QApplication, \
    QHBoxLayout, QHeaderView, QAbstractItemView, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
import math

from qgis.core import QgsRasterLayer,QgsVectorLayer, QgsProject, QgsVectorTileLayer  # Import QGIS classes

from .TransactionApiDialog import TransactionApiDialog


class DataDistributionDialog(QDialog):
    def __init__(self, dataType, data_url , dump_url=None):
        super().__init__()

        self.allowedFileTypes = ["geojson" , "kml" , "filegdb" , "shp"]
        self.setWindowTitle(dataType.replace('_', ' ').title())
        self.data_url = data_url
        self.dump_url = dump_url
        self.dataType = dataType

        self.load_data()

    def create_ui(self, columns,columnCount):
        main_layout = QVBoxLayout()

        # Table View
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(columnCount)  # Increase column count to 5
        self.table_widget.setHorizontalHeaderLabels(columns)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table_widget)

        # Close Button
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)

        self.setLayout(main_layout)

    def load_data(self):
        try:
            response = requests.get(self.data_url, verify=False)
            data = response.json()
            if self.dataType == "cached_map_tiles":
                self.create_ui(['Name', 'URL', '', 'Add to Map'], 4)
                self.populate_table_for_cached_map_tiles(data)
            elif self.dataType == "transactional_api":
                self.create_ui(['ID', 'Name', 'URL', 'Publish'], 4)
                self.populate_table_for_transactional_api(data)
            elif self.dataType == "FileList":
                self.create_ui(['Name', 'URL', '', 'Publish'], 4)
                self.populate_table_for_statis_gis_files(data)
            elif self.dataType == "COGEndpoint":
                self.create_ui(['Name', 'URL', '', 'Publish'], 4)
                self.populate_table_for_cog(data)
            else:
                self.create_ui(['Name', 'URL', 'Size', ''], 4)
                self.populate_table(data)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Error fetching data: {e}")

    def populate_table_for_cached_map_tiles(self, data):
        self.table_widget.setRowCount(len(data))
        for row, item in enumerate(data):
            name_item = QTableWidgetItem(item['name'])
            url_item = QTableWidgetItem(item['tileURL'])

            url_item.setFlags(url_item.flags() | Qt.ItemIsEditable)

            self.table_widget.setItem(row, 0, name_item)
            self.table_widget.setItem(row, 1, url_item)

            # Copy URL Button
            copy_button = QPushButton('Copy URL')
            copy_button.clicked.connect(lambda _, r=row: self.copy_url(r))
            self.table_widget.setCellWidget(row, 2, copy_button)

            # Add to Map Button
            add_map_button = QPushButton('Add to Map')
            add_map_button.clicked.connect(lambda _, r=row: self.add_vector_tiles_layer_to_map(r))
            self.table_widget.setCellWidget(row, 3, add_map_button)

        self.table_widget.resizeColumnsToContents()
        self.adjust_dialog_size()

    def populate_table_for_statis_gis_files(self, data):
        self.table_widget.setRowCount(len(data))
        for row, item in enumerate(data):
            name_item = QTableWidgetItem(item['name'])
            url_item = QTableWidgetItem(item['url'])
            # size_item = QTableWidgetItem(str(self.convert_size(item['size'])))

            url_item.setFlags(url_item.flags() | Qt.ItemIsEditable)

            self.table_widget.setItem(row, 0, name_item)
            self.table_widget.setItem(row, 1, url_item)
            # self.table_widget.setItem(row, 2, size_item)

            # Copy URL Button
            copy_button = QPushButton('Copy URL')
            copy_button.clicked.connect(lambda _, r=row: self.copy_url(r))
            self.table_widget.setCellWidget(row, 2, copy_button)

            # Add to Map Button
            add_map_button = QPushButton('Add to Map')
            add_map_button.clicked.connect(lambda _, r=row: self.add_static_file_to_map(r))
            self.table_widget.setCellWidget(row, 3, add_map_button)

        self.table_widget.resizeColumnsToContents()
        self.adjust_dialog_size()

    def populate_table_for_cog(self, data):
        filtered_data = [item for item in data if item['name'].lower().endswith(('.tif', '.tiff'))]
        self.table_widget.setRowCount(len(filtered_data))

        for row, item in enumerate(filtered_data):
            name_item = QTableWidgetItem(item['name'])
            # url = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/Q/WD/2020/7/S2A_36QWD_20200701_0_L2A/TCI.tif"
            # url = "http://oin-hotosm.s3.amazonaws.com/59d33df023c8440011d7b26d/0/b378087a-c2a5-43a0-abec-71fcfb051150.tif"
            url = item['url']
            url_item = QTableWidgetItem(url)
            # Make URL editable
            url_item.setFlags(url_item.flags() | Qt.ItemIsEditable)

            self.table_widget.setItem(row, 0, name_item)
            self.table_widget.setItem(row, 1, url_item)

            # Copy URL Button
            copy_button = QPushButton('Copy URL')
            copy_button.clicked.connect(lambda _, r=row: self.copy_url(r))
            self.table_widget.setCellWidget(row, 2, copy_button)

            # Add to Map Button
            add_map_button = QPushButton('Add to Map')
            add_map_button.clicked.connect(lambda _, r=row: self.add_cog_to_map(r))
            self.table_widget.setCellWidget(row, 3, add_map_button)

        self.table_widget.resizeColumnsToContents()
        self.adjust_dialog_size()

    def populate_table_for_transactional_api(self, data):
        self.table_widget.setRowCount(len(data))
        rowNumber = 0
        for row, item in enumerate(data):
            fileType = item['format']
            if fileType in self.allowedFileTypes:
                name_item = QTableWidgetItem(item['name'])
                url_item = QTableWidgetItem(item['url'])

                url_item.setFlags(url_item.flags() | Qt.ItemIsEditable)

                self.table_widget.setItem(rowNumber, 0, name_item)
                self.table_widget.setItem(rowNumber, 1, url_item)

                # Copy URL Button
                copy_button = QPushButton('Copy URL')
                copy_button.clicked.connect(lambda _, r=rowNumber: self.copy_url(r))
                self.table_widget.setCellWidget(rowNumber, 2, copy_button)

                # Add to Map Button
                add_map_button = QPushButton('Publish')
                add_map_button.clicked.connect(lambda _, r=rowNumber: self.publish(r))
                self.table_widget.setCellWidget(rowNumber, 3, add_map_button)
                rowNumber = rowNumber + 1
        self.table_widget.setRowCount(rowNumber)
        self.table_widget.resizeColumnsToContents()
        self.adjust_dialog_size()


    def populate_table(self, data):
        self.table_widget.setRowCount(len(data))
        for row, item in enumerate(data):
            name_item = QTableWidgetItem(item['name'])
            url_item = QTableWidgetItem(item['url'])
            # size_item = QTableWidgetItem(str(self.convert_size(item['size'])))

            url_item.setFlags(url_item.flags() | Qt.ItemIsEditable)

            self.table_widget.setItem(row, 0, name_item)
            self.table_widget.setItem(row, 1, url_item)
            # self.table_widget.setItem(row, 2, size_item)

            # Copy URL Button
            copy_button = QPushButton('Copy URL')
            copy_button.clicked.connect(lambda _, r=row: self.copy_url(r))
            self.table_widget.setCellWidget(row, 2, copy_button)

            # Add to Map Button
            # add_map_button = QPushButton('Add to Map')
            # add_map_button.clicked.connect(lambda _, r=row: self.add_raster_layer_to_map(r))
            # self.table_widget.setCellWidget(row, 4, add_map_button)

        self.table_widget.resizeColumnsToContents()
        self.adjust_dialog_size()

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def adjust_dialog_size(self):
        self.table_widget.setMinimumWidth(self.table_widget.horizontalHeader().length())
        self.table_widget.setMinimumHeight(self.table_widget.verticalHeader().length() + self.table_widget.horizontalHeader().height())

        # Adjust the dialog size based on the table content
        width = self.table_widget.horizontalHeader().length() + self.table_widget.verticalHeader().width() + 20  # Additional padding
        height = self.table_widget.verticalHeader().length() + self.table_widget.horizontalHeader().height() + 80  # Additional padding for header and layout
        self.resize(width, height)

    def copy_url(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        print(f"Copied URL: {url}")
    def add_vector_tiles_layer_to_map(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()

        name_item = self.table_widget.item(row, 0)
        name = url_item.text()
        url = f'type=xyz&url={url}'
        vector_tile_layer = QgsVectorTileLayer(url, name)

        if not vector_tile_layer.isValid():
            QMessageBox.critical(self, 'Error', 'Failed to load the vector tile layer.')
        else:
            QgsProject.instance().addMapLayer(vector_tile_layer)
            QMessageBox.information(self, 'Success', 'Vector tile layer added to the map.')


    def publish(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()

        # Create an instance of the dialog
        dialog = TransactionApiDialog(url, self.dump_url)

        # Open the dialog
        dialog.exec_()
        # name_item = self.table_widget.item(row, 0)
        # name = url_item.text()
        # url = f'type=xyz&url={url}'
        # vector_tile_layer = QgsVectorTileLayer(url, name)
        #
        # if not vector_tile_layer.isValid():
        #     QMessageBox.critical(self, 'Error', 'Failed to load the vector tile layer.')
        # else:
        #     QgsProject.instance().addMapLayer(vector_tile_layer)
        #     QMessageBox.information(self, 'Success', 'Vector tile layer added to the map.')


    def add_raster_layer_to_map(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()

        # Create and add the raster layer to the QGIS map canvas
        raster_layer = QgsRasterLayer(url, url.split('/')[-1])
        if raster_layer.isValid():
            QgsProject.instance().addMapLayer(raster_layer)
            print(f"Added Raster Layer: {url}")
        else:
            QMessageBox.critical(self, f"Failed to add Raster Layer: {url}")

    def add_static_file_to_map(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()

        # Create and add the raster layer to the QGIS map canvas
        vector_layer = QgsVectorLayer(url, url.split('/')[-1], 'ogr')
        if vector_layer.isValid():
            QgsProject.instance().addMapLayer(vector_layer)
            print(f"Added KML Vector Layer: {url}")
        else:
            QMessageBox.critical(self, 'Error', f"Failed to add KML Vector Layer: {url}")

    def add_cog_to_map(self, row):
        url_item = self.table_widget.item(row, 1)
        url = url_item.text()

        # Add the raster layer using the URL protocol
        raster_layer = QgsRasterLayer(f"/vsicurl/{url}", url.split('/')[-1], 'gdal')
        # raster_layer = QgsRasterLayer(url, url.split('/')[-1])
        if raster_layer.isValid():
            QgsProject.instance().addMapLayer(raster_layer)
            print(f"Added COG Raster Layer via URL: {url}")
        else:
            QMessageBox.critical(self, 'Error', f"Failed to add COG Raster Layer via URL: {url}")

