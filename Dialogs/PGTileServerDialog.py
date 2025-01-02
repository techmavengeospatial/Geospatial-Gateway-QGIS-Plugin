from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
import requests
from qgis.core import QgsProject, QgsVectorTileLayer

class PGTileServerDialog(QDialog):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Dynamic Vector Tiles')

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Table for displaying data
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Description', 'Details'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Verify and load the JSON from the URL
        if not self.verify_and_load_url(url):
            self.close()

    def verify_and_load_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):  # Assuming the JSON is a dictionary with key-value pairs
                self.populate_table(data)
                return True
            else:
                QMessageBox.warning(self, 'Invalid JSON', 'The JSON does not have the expected format.')
                return False
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch URL: {e}')
            return False
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The URL did not return a valid JSON.')
            return False

    def populate_table(self, data):
        self.table.setRowCount(0)
        for key, value in data.items():
            id_item = QTableWidgetItem(value.get('id', ''))
            name_item = QTableWidgetItem(value.get('name', ''))
            description_item = QTableWidgetItem(value.get('description', ''))
            
            details_button = QPushButton('Details')
            details_button.clicked.connect(lambda _, url=value.get('detailurl', ''): self.open_details_dialog(url))
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, description_item)
            self.table.setCellWidget(row, 3, details_button)

    def open_details_dialog(self, detailurl):
        if detailurl:
            dialog = TileDetailsDialog(detailurl, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, 'No Details', 'No detail URL available for this item.')

class TileDetailsDialog(QDialog):
    def __init__(self, detailurl, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Tile Details')

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Display the details URL
        self.details_label = QLabel(f'Detail URL: {detailurl}', self)
        self.layout.addWidget(self.details_label)

        # Table for displaying tile details
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Name', 'Add to Map'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Load and populate the table
        if not self.load_and_populate_table(detailurl):
            self.close()

    def load_and_populate_table(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                QMessageBox.warning(self, 'Invalid JSON', 'The JSON does not have the expected format.')
                return False

            self.populate_table(data)
            return True
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch URL: {e}')
            return False
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The URL did not return a valid JSON.')
            return False

    def populate_table(self, data):
        self.table.setRowCount(0)
        # for item in data.get('tiles', []):
        name = data.get('name', '')
        tileurl = data.get('tileurl', '')

        name_item = QTableWidgetItem(name)

        add_button = QPushButton('Add to Map')
        add_button.clicked.connect(lambda _, url=tileurl, layer_name=name: self.add_to_map(url, layer_name))

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, name_item)
        self.table.setCellWidget(row, 1, add_button)

    def add_to_map(self, tileurl, name):
        url = f'type=xyz&url={tileurl}'
        vector_tile_layer = QgsVectorTileLayer(url, name)

        if not vector_tile_layer.isValid():
            QMessageBox.critical(self, 'Error', 'Failed to load the vector tile layer.')
        else:
            QgsProject.instance().addMapLayer(vector_tile_layer)
            QMessageBox.information(self, 'Success', 'Vector tile layer added to the map.')
