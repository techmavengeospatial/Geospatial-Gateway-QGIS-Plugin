import json
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout,QGridLayout,QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,QComboBox
import requests

from .DatabaseConnectionDialog import DatabaseConnectionDialog


class TSConfigurationsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Plugin Configurations')
        self.config_file = os.path.join(os.path.dirname(__file__), 'configurations.json')
        self.databaseDlg = DatabaseConnectionDialog()

        self.create_ui()
        self.load_configurations()

    def create_ui(self):
        main_layout = QVBoxLayout()

        # Tile Server URL, Port, and Fetch URL Buttons in Horizontal Layout
        tile_server_layout = QVBoxLayout()
        self.tile_server_url_input = QLineEdit()
        tile_server_layout.addWidget(QLabel('Tile Server URL'))
        tile_server_layout.addWidget(self.tile_server_url_input)
        self.tile_server_url_input.setMinimumWidth(500)  # Adjust the value as needed

        self.tile_server_port_input = QLineEdit()
        tile_server_layout.addWidget(QLabel('Tile Server Port'))
        tile_server_layout.addWidget(self.tile_server_port_input)

        fetch_url_buttons = QPushButton('Fetch Urls')
        fetch_url_buttons.clicked.connect(self.fetchUrls)
        tile_server_layout.addWidget(fetch_url_buttons)

        main_layout.addLayout(tile_server_layout)

        # Grid Layout for Two-Column Input Fields
        grid_layout = QGridLayout()

        # Add rows for each input field (left and right columns)
        self.connection_dropdown = QComboBox()
        grid_layout.addWidget(QLabel('PostGIS Connections:'), 0, 0)
        grid_layout.addWidget(self.connection_dropdown, 0, 1)
        add_button = QPushButton("Add New")
        add_button.clicked.connect(self.add_new_connection)
        grid_layout.addWidget(add_button, 0, 2)

        grid_layout.addWidget(QLabel('Collection Forms Builder'), 1, 0)
        self.collection_form_builder_input = QLineEdit()
        grid_layout.addWidget(self.collection_form_builder_input, 1, 1,1, 2)

        grid_layout.addWidget(QLabel('Team Collaboration Application'), 2, 0)
        self.team_collaboration_input = QLineEdit()
        grid_layout.addWidget(self.team_collaboration_input, 2, 1,1, 2)

        grid_layout.addWidget(QLabel('Catalog Generator'), 3, 0)
        self.catalog_generator_input = QLineEdit()
        grid_layout.addWidget(self.catalog_generator_input, 3, 1,1, 2)

        grid_layout.addWidget(QLabel('Discover'), 4, 0)
        self.discover_input = QLineEdit()
        grid_layout.addWidget(self.discover_input, 4, 1,1, 2)

        grid_layout.addWidget(QLabel('3D Map (Terriajs)'), 5, 0)
        self.map_3d_terriajs_input = QLineEdit()
        grid_layout.addWidget(self.map_3d_terriajs_input, 5, 1,1, 2)

        grid_layout.addWidget(QLabel('2D Map (Open Layers)'), 6, 0)
        self.map_2d_open_layers_input = QLineEdit()
        grid_layout.addWidget(self.map_2d_open_layers_input, 6, 1,1, 2)

        grid_layout.addWidget(QLabel('Edge Team Collaboration Module'), 7, 0)
        self.edge_team_collaboration_input = QLineEdit()
        grid_layout.addWidget(self.edge_team_collaboration_input, 7, 1,1, 2)

        grid_layout.addWidget(QLabel('OGC API Feature'), 8, 0)
        self.ogc_api_feature_input = QLineEdit()
        grid_layout.addWidget(self.ogc_api_feature_input, 8, 1,1, 2)

        grid_layout.addWidget(QLabel('Dynamic Vector Tiles'), 9, 0)
        self.dynamic_vector_tiles_input = QLineEdit()
        grid_layout.addWidget(self.dynamic_vector_tiles_input, 9, 1,1, 2)

        grid_layout.addWidget(QLabel('COG Endpoint'), 10, 0)
        self.cog_endpoint_input = QLineEdit()
        grid_layout.addWidget(self.cog_endpoint_input, 10, 1,1, 2)

        grid_layout.addWidget(QLabel('MBTiles Distribution'), 11, 0)
        self.mbtiles_distribution_input = QLineEdit()
        grid_layout.addWidget(self.mbtiles_distribution_input, 11, 1,1, 2)

        grid_layout.addWidget(QLabel('GPKGs Distribution'), 12, 0)
        self.gpkgs_distribution_input = QLineEdit()
        grid_layout.addWidget(self.gpkgs_distribution_input, 12, 1,1, 2)

        grid_layout.addWidget(QLabel('Style Download'), 13, 0)
        self.style_download_input = QLineEdit()
        grid_layout.addWidget(self.style_download_input, 13, 1,1, 2)

        grid_layout.addWidget(QLabel('Cached Map Tiles'), 14, 0)
        self.cached_map_tiles_input = QLineEdit()
        grid_layout.addWidget(self.cached_map_tiles_input, 14, 1,1, 2)

        grid_layout.addWidget(QLabel('Statis GIS Files'), 15, 0)
        self.file_list_input = QLineEdit()
        grid_layout.addWidget(self.file_list_input, 15, 1,1, 2)

        grid_layout.addWidget(QLabel('Upload URL'), 16, 0)
        self.upload_url_input = QLineEdit()
        grid_layout.addWidget(self.upload_url_input, 16, 1,1, 2)

        grid_layout.addWidget(QLabel('Transactional Api'), 17, 0)
        self.transactional_api_url_input = QLineEdit()
        grid_layout.addWidget(self.transactional_api_url_input, 17, 1, 1, 2)

        grid_layout.addWidget(QLabel('Transactional Api Upload File'), 18, 0)
        self.transactional_api_upload_url_input = QLineEdit()
        grid_layout.addWidget(self.transactional_api_upload_url_input, 18, 1, 1, 2)

        grid_layout.addWidget(QLabel('Pocketbase'), 19, 0)
        self.pocketbase_input = QLineEdit()
        grid_layout.addWidget(self.pocketbase_input, 19, 1, 1, 2)

        # Add the grid layout to the main layout
        main_layout.addLayout(grid_layout)

        # Save Button
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_configurations)
        main_layout.addWidget(save_button)

        self.setLayout(main_layout)
        self.loadConnections()
    def loadConnections(self):
        config_data = self.load_database_configurations()
        postgres_configs = config_data.get("ToPostgisDirect", [])
        self.connection_dropdown.clear()
        for config in postgres_configs:
            self.connection_dropdown.addItem(config.get("project_name", "Unnamed"))

    def load_database_configurations(self):
        with open(self.config_file, 'r') as config_file:
            return json.load(config_file)

    def edit_connection(self):
        selected_connection = self.connection_dropdown.currentText()
        # Logic to edit the selected connection
        # You can display another dialog to edit the details of the selected connection
        print(f"Editing connection: {selected_connection}")

    def add_new_connection(self):
        self.databaseDlg.exec_()
        self.loadConnections()

    def fetchUrls(self):
        # Get the base URL and port
        tsUrl = self.tile_server_url_input.text()
        tsPort = self.tile_server_port_input.text()

        # Construct the URL
        full_url = f"{tsUrl}:{tsPort}/index.json"

        # try:
            # Fetch the JSON data
        print(full_url)
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        # print(data)
        # Create a mapping of names to inputs
        input_mapping = {
            "Discover": self.discover_input,
            "UploadFile": self.upload_url_input,
            "MBTilesDistribution": self.mbtiles_distribution_input,
            "Files": self.file_list_input,
            "DynamicVT": self.dynamic_vector_tiles_input,
            "Services":self.cached_map_tiles_input,
            "TerriMap": self.map_3d_terriajs_input,
            "OGCAPI": self.ogc_api_feature_input,
            "EdgeTeamCollaboration": self.edge_team_collaboration_input,
            "PocketBase": self.pocketbase_input,
            "OLMap": self.map_2d_open_layers_input,
            "COGEndpoint": self.cog_endpoint_input,
            "GPKGsDistribution": self.gpkgs_distribution_input,
            "StylesDownload": self.style_download_input,
            "TransactionalAPI":self.transactional_api_url_input,
            "TransactionalAPI_Upload": self.transactional_api_upload_url_input,
        }

        def get_case_insensitive_key(item, key):
            return next((item[k] for k in item if k.lower() == key.lower()), None)
        # Populate inputs
        for item in data:
            name = get_case_insensitive_key(item, "name")
            url = get_case_insensitive_key(item, "url")
            if name in input_mapping:
                input_mapping[name].setText(url)

        # except requests.exceptions.RequestException as e:
        #     # Show an error message if the request fails
        #     QMessageBox.critical(self, "Error", f"Failed to fetch data: {e}")
        # except ValueError:
        #     # Handle JSON decoding errors
        #     QMessageBox.critical(self, "Error", "Invalid JSON response.")

    def load_configurations(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                self.collection_form_builder_input.setText(config.get('CollectionFormsBuilder', ''))
                self.team_collaboration_input.setText(config.get('TeamCollaborationApplication', ''))
                self.catalog_generator_input.setText(config.get('CatalogGenerator', ''))
                self.discover_input.setText(config.get('Discover', ''))
                self.map_3d_terriajs_input.setText(config.get('Map3DTerriajs', ''))
                self.map_2d_open_layers_input.setText(config.get('Map2DOpenLayers', ''))
                self.edge_team_collaboration_input.setText(config.get('EdgeTeamCollaborationModule', ''))

                # Load additional configuration fields
                self.ogc_api_feature_input.setText(config.get('OGCApiFeature', ''))
                self.dynamic_vector_tiles_input.setText(config.get('DynamicVectorTiles', ''))
                self.cog_endpoint_input.setText(config.get('COGEndpoint', ''))
                self.cached_map_tiles_input.setText(config.get('CachedMapTiles', ''))

                # Load new fields for Tile Server and Upload URLs
                self.tile_server_url_input.setText(config.get('TileServerUrl', ''))
                self.tile_server_port_input.setText(config.get('TileServerPort', ''))
                self.upload_url_input.setText(config.get('UploadUrl', ''))
                self.transactional_api_url_input.setText(config.get('TransactionalAPI', ''))
                self.transactional_api_upload_url_input.setText(config.get('TransactionalAPI_Upload', ''))
                self.pocketbase_input.setText(config.get('PocketBase', ''))
                self.file_list_input.setText(config.get('FileList', ''))
                self.mbtiles_distribution_input.setText(config.get('MBTilesDistribution', ''))
                self.gpkgs_distribution_input.setText(config.get('GPKGsDistribution', ''))
                self.style_download_input.setText(config.get('StylesDownload', ''))


    def save_configurations(self):
        # Load existing config or create a new one if it doesn't exist
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}

        # Update config with new values
        config.update({
            'CollectionFormsBuilder': self.collection_form_builder_input.text(),
            'TeamCollaborationApplication': self.team_collaboration_input.text(),
            'CatalogGenerator': self.catalog_generator_input.text(),
            'Discover': self.discover_input.text(),
            'Map3DTerriajs': self.map_3d_terriajs_input.text(),
            'Map2DOpenLayers': self.map_2d_open_layers_input.text(),
            'EdgeTeamCollaborationModule': self.edge_team_collaboration_input.text(),
            'OGCApiFeature': self.ogc_api_feature_input.text(),
            'DynamicVectorTiles': self.dynamic_vector_tiles_input.text(),
            'COGEndpoint': self.cog_endpoint_input.text(),
            'CachedMapTiles': self.cached_map_tiles_input.text(),
            'TileServerUrl': self.tile_server_url_input.text(),
            'TileServerPort': self.tile_server_port_input.text(),
            'UploadUrl': self.upload_url_input.text(),
            'TransactionalAPI': self.transactional_api_url_input.text(),
            'TransactionalAPI_Upload': self.transactional_api_upload_url_input.text(),
            'PocketBase': self.pocketbase_input.text(),
            'FileList': self.file_list_input.text(),
            'MBTilesDistribution': self.mbtiles_distribution_input.text(),
            'GPKGsDistribution': self.gpkgs_distribution_input.text(),
            'StylesDownload': self.style_download_input.text()
        })

        # Save the updated configuration back to the file
        with open(self.config_file, 'w') as file:
            json.dump(config, file, indent=4)

        QMessageBox.information(self, 'Success', 'Configurations saved successfully!')
