from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
import requests
from qgis.core import QgsVectorLayer, QgsProject

class PGFeatureServerDialog(QDialog):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle('OGC API Features')

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Table for displaying collections
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Title', 'Description', 'Add to Map'])
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
            if 'collections' in data:
                self.populate_table(data['collections'])
                return True
            else:
                QMessageBox.warning(self, 'Invalid JSON', 'The JSON does not contain "collections".')
                return False
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch URL: {e}')
            return False
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The URL did not return a valid JSON.')
            return False

    def populate_table(self, collections):
        self.table.setRowCount(0)
        for i, collection in enumerate(collections):
            id_item = QTableWidgetItem(collection.get('id', ''))
            title_item = QTableWidgetItem(collection.get('title', ''))
            description_item = QTableWidgetItem(collection.get('description', ''))

            add_button = QPushButton('Add to Map')
            add_button.clicked.connect(lambda _, row=i: self.add_to_map(collections[row]))

            self.table.insertRow(i)
            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, title_item)
            self.table.setItem(i, 2, description_item)
            self.table.setCellWidget(i, 3, add_button)

    def add_to_map(self, collection):
        links = collection.get('links', [])
        geojson_url = next((link['href'] for link in links if link.get('type') == 'application/geo+json'), None)
        print(geojson_url)
        if geojson_url:
            layer = QgsVectorLayer(geojson_url, collection.get('title', 'Unnamed Layer'), 'ogr')
            if not layer.isValid():
                QMessageBox.critical(self, 'Error', 'Failed to load the GeoJSON layer.')
            else:
                QgsProject.instance().addMapLayer(layer)
        else:
            QMessageBox.warning(self, 'No GeoJSON', 'No GeoJSON link found in the collection.')
