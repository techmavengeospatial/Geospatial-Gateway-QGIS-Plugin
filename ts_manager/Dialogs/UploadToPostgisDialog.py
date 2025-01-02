from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import json
from qgis.core import QgsVectorLayer, QgsVectorLayerExporter, QgsCoordinateReferenceSystem
import os

from sshtunnel import SSHTunnelForwarder


class UploadToPostgisDialog(QDialog):
    def __init__(self, is_ssh , parent=None):
        super().__init__(parent)
        self.setWindowTitle('Upload to PostGIS Direct')
        self.is_ssh = is_ssh
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),'configurations.json')# Load the existing configuration file
        # Load configurations from JSON
        self.configurations = self.load_configurations(self.config_file)
        if not self.configurations:
            QMessageBox.critical(self, 'Error', 'Failed to load configurations.')
            self.close()
            return

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Database connections dropdown
        self.connection_dropdown = QComboBox(self)
        self.populate_connections()
        self.layout.addWidget(QLabel('Select Database Connection:'))
        self.layout.addWidget(self.connection_dropdown)

        # File browser for shapefile or GeoJSON
        self.browse_button = QPushButton('Browse Shapefile/GeoJSON', self)
        self.browse_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.browse_button)

        # Load to database button
        self.load_button = QPushButton('Load into Database', self)
        self.load_button.clicked.connect(self.load_into_database)
        self.layout.addWidget(self.load_button)

        # Placeholder for the selected file path
        self.shapefile_path = None

    def load_configurations(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
            return config.get('ToPostgisDirect', [])
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading configurations: {e}")
            return None

    def populate_connections(self):
        for connection in self.configurations:
            self.connection_dropdown.addItem(connection.get('project_name'), connection)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Shapefile or GeoJSON', '', 'Shapefile (*.shp);;GeoJSON (*.geojson)')
        if file_path:
            self.shapefile_path = file_path
            self.browse_button.setText(f'Selected: {file_path}')

    def load_into_database(self):
        if not self.shapefile_path:
            QMessageBox.warning(self, 'No File Selected', 'Please select a shapefile or GeoJSON file.')
            return

        selected_connection = self.connection_dropdown.currentData()
        if not selected_connection:
            QMessageBox.warning(self, 'No Connection Selected', 'Please select a database connection.')
            return

        host = selected_connection['host']
        port = selected_connection['port']
        database = selected_connection['database']
        user = selected_connection['user']
        password = selected_connection['password']
        table_name = self.generate_table_name(self.shapefile_path)

        # Check if SSH is needed
        # is_ssh = 'ssh_host' in selected_connection

        if self.is_ssh:
            ssh_host = selected_connection['ssh_host']
            ssh_port = selected_connection['ssh_port']
            ssh_user = selected_connection['ssh_user']
            ssh_password = selected_connection['ssh_password']

            with SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_password=ssh_password,
                    remote_bind_address=(host, int(port)),
                    local_bind_address=('localhost', 5433)  # You can choose any free local port
            ) as tunnel:
                local_host = 'localhost'
                local_port = tunnel.local_bind_port

                con_string = f"dbname='{database}' host='{local_host}' port='{local_port}' user='{user}' password='{password}' key=id table='{table_name}' (geom)"

                self._export_layer_to_postgis(con_string, table_name)
        else:
            con_string = f"dbname='{database}' host='{host}' port='{port}' user='{user}' password='{password}' key=id table='{table_name}' (geom)"

            self._export_layer_to_postgis(con_string, table_name)

    def _export_layer_to_postgis(self, con_string, table_name):
        layer = QgsVectorLayer(self.shapefile_path, table_name, "ogr")
        if not layer.isValid():
            QMessageBox.critical(self, 'Error', 'Failed to load the selected file as a layer.')
            return

        self.execute_sql_sa(f'DROP TABLE IF EXISTS "{table_name}"')

        err = QgsVectorLayerExporter.exportLayer(layer, con_string, 'postgres',
                                                 QgsCoordinateReferenceSystem(layer.sourceCrs()), False)

        if err[0] != QgsVectorLayerExporter.NoError:
            QMessageBox.critical(self, 'Error', f'Failed to export the layer to PostGIS: {err[1]}')
        else:
            QMessageBox.information(self, 'Success', 'Layer successfully added to the PostGIS database.')

    def generate_table_name(self, file_path):
        import os
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        return table_name.replace(" ", "_").replace("-", "_").lower()

    def execute_sql_sa(self, sql):
        # Implement the SQL execution logic here
        print(f"Executing SQL: {sql}")
        # The actual implementation will depend on your database connection setup
