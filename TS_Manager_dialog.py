from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout,QGridLayout, QPushButton, QComboBox,QCheckBox,QHBoxLayout, QLabel, QMessageBox,QAction, QMessageBox, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsProject
import json
import os
from urllib.parse import urljoin
import psycopg2

from .Dialogs.ProjectToPostgis import ProjectToPostgis
from .Dialogs.LoadProjectFromPostgis import LoadProjectFromPostgis
from .Dialogs.MetadataManagerDialog import MetadataManagerDialog
from .Dialogs.DataDistributionDialog import DataDistributionDialog
from .Dialogs.PGFeatureServerDialog import PGFeatureServerDialog
from .Dialogs.PGTileServerDialog import PGTileServerDialog
from .Dialogs.UploadStaticFileDialog import UploadStaticFileDialog
from .TSConfigurationsDialog import TSConfigurationsDialog
from .Dialogs.OpenWebView import OpenWebView

class TSManagerDialog(QDialog):
    def __init__(self,iface , loginDialog):
        super(TSManagerDialog, self).__init__()
        self.iface = iface
        self.setWindowTitle("Tile Server Manager")
        self.loginDialog = loginDialog
        # Set background color and window size
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setFixedSize(1200, 500)

        script_dir = os.path.dirname(os.path.realpath(__file__))

        self.config_file = os.path.join(os.path.dirname(__file__),
                                        'configurations.json')  # Load the existing configuration file
        self.configurations = self.load_configurations(self.config_file)
        if not self.configurations:
            QMessageBox.critical(self, 'Error', 'Failed to load configurations.')
            self.close()
            return

        # panels
        topHorizontalPanel = QHBoxLayout()
        middlePanel = QHBoxLayout()
        webviewVerticalPanel = QVBoxLayout()
        tileServerPanel = QGridLayout()

        topHorizontalPanel.setSpacing(20)



        # Panel 2 layout with 3 layouts  - webview ,tileserver and logout button


        # configuration button
        config_btn = QPushButton("Configurations")
        meta_data_btn = QPushButton("Meta Data")
        # Webview Buttons
        pocketbase_collection_formbuilder_webview_btn = QPushButton("Collection Forms Builder")
        # team_collaboration_app_webview_btn = QPushButton("Team Collaboration Application")
        catalog_generator_webview_btn = QPushButton("Catalog Generator")
        discover_webview_btn = QPushButton("Discover")
        terria3d_webview_btn = QPushButton("3D Map (Terriajs)")
        openlayers2d_webview_btn = QPushButton("2D Map (Open Layers)  ")
        edge_team_collaboration_webview_btn = QPushButton("Edge Team Collaboration Module")
        # Tile server and logout button
        upl_files = QPushButton("Upload files: MBTiles, COG, Files, 3dtiles, Catalog, GPKG, Styles, Others")
        proj_to_postgis = QPushButton("Project To PostGIS")
        load_proj_from_postgis = QPushButton("Load Project From PostGIS")
        transactional_api_btn = QPushButton("Transactional API")
        transactional_api_upload_btn = QPushButton("Transactional API Upload")
        file_list_api_btn = QPushButton("Static GIS File")
        pg_fs_btn = QPushButton("OGC API FEATURES")
        pg_ts_btn = QPushButton("Dynamic Vector Tiles")
        data_mbtile_distributon_endp = QPushButton("MBTiles Distribution")
        data_gpkg_distributon_endp = QPushButton("GPKG Distribution")
        data_style_distributon_endp = QPushButton("Styles Distribution")
        data_cog_endp = QPushButton("COG Endpoint")
        data_cached_ms = QPushButton("Cached Map Tiles")

        logout_btn = QPushButton("Logout")

        webview_label = QLabel("Web Views")
        webview_label.setFont(QFont("Arial", 16, QFont.Bold))
        webview_label.setStyleSheet("color: #333333; padding-bottom: 10px;")

        tileserver_label = QLabel("Tile Server")
        tileserver_label.setFont(QFont("Arial", 16, QFont.Bold))
        tileserver_label.setStyleSheet("color: #333333; padding-bottom: 10px;")


        tsUrl = "https://techmaven.net/portabletileserver/windows-tile-server/"
        pocketbase_collection_formbuilder_webview_btn.clicked.connect(
            lambda: self.openWebView("Collection Forms Builder", "CollectionFormsBuilder"))
        # team_collaboration_app_webview_btn.clicked.connect(
        #     lambda: self.openWebView("Team Collaboration Application", "TeamCollaborationApplication"))
        catalog_generator_webview_btn.clicked.connect(lambda: self.openWebView("Catalog Generator", "CatalogGenerator"))
        discover_webview_btn.clicked.connect(lambda: self.openWebView("Discover", "Discover"))
        terria3d_webview_btn.clicked.connect(lambda: self.openWebView("Map 3D Terriajs", "Map3DTerriajs"))
        openlayers2d_webview_btn.clicked.connect(lambda: self.openWebView("Openlayers Map", "Map2DOpenLayers"))
        edge_team_collaboration_webview_btn.clicked.connect(
            lambda: self.openWebView("Edge Team Collaboration Module", "EdgeTeamCollaborationModule"))

        pg_fs_btn.clicked.connect(self.pgFeatureServer)
        pg_ts_btn.clicked.connect(self.pgTileServer)
        # data_cog_endp.clicked.connect(self.showCogEndPoint)
        data_cog_endp.clicked.connect(lambda: self.showDataDistribution("COGEndpoint"))
        data_mbtile_distributon_endp.clicked.connect(lambda: self.showDataDistribution("MBTilesDistribution"))
        data_gpkg_distributon_endp.clicked.connect(lambda: self.showDataDistribution("GPKGsDistribution"))
        data_style_distributon_endp.clicked.connect(lambda: self.showDataDistribution("StylesDownload"))


        data_cached_ms.clicked.connect(self.showCachedMapTiles)
        transactional_api_btn.clicked.connect(self.showTransactionalApi)
        transactional_api_upload_btn.clicked.connect(self.showTransactionalApiUpload)
        file_list_api_btn.clicked.connect(lambda: self.showDataDistribution("FileList"))
        upl_files.clicked.connect(self.uploadStaticFile)
        proj_to_postgis.clicked.connect(self.projToPostgis)
        load_proj_from_postgis.clicked.connect(self.loadProjFromPostgis)

        config_btn.clicked.connect(self.openConfigurations)
        meta_data_btn.clicked.connect(self.openMetaDataManager)
        logout_btn.clicked.connect(self.logout)




        # topHorizontalPanel.addWidget(config_btn)
        # topHorizontalPanel.addWidget(meta_data_btn)
        # webviewVerticalPanel.addWidget(webview_label)
        # webviewVerticalPanel.addWidget(pocketbase_collection_formbuilder_webview_btn)
        # webviewVerticalPanel.addWidget(edge_team_collaboration_webview_btn)
        # webviewVerticalPanel.addWidget(openlayers2d_webview_btn)
        # webviewVerticalPanel.addWidget(terria3d_webview_btn)
        # webviewVerticalPanel.addWidget(discover_webview_btn)
        # webviewVerticalPanel.addWidget(catalog_generator_webview_btn)
        # # webviewVerticalPanel.addWidget(team_collaboration_app_webview_btn)
        # tileServerPanel.addWidget(tileserver_label,0,0)
        # tileServerPanel.addWidget(upl_files,1,0,1,4)
        # tileServerPanel.addWidget(transactional_api_upload_btn, 2, 0, 1, 2)
        # tileServerPanel.addWidget(transactional_api_btn, 2, 2, 1, 2)
        # tileServerPanel.addWidget(data_mbtile_distributon_endp, 3, 0,1,2)
        # tileServerPanel.addWidget(data_gpkg_distributon_endp, 3, 2,1,2)
        # tileServerPanel.addWidget(data_style_distributon_endp, 4, 0,1,2)
        # tileServerPanel.addWidget(file_list_api_btn, 4, 2,1,2)
        # tileServerPanel.addWidget(data_cog_endp, 5, 0,1,2)
        # tileServerPanel.addWidget(data_cached_ms, 5, 2,1,2)
        # tileServerPanel.addWidget(proj_to_postgis,6,0,1,2)
        # tileServerPanel.addWidget(pg_fs_btn,7,0,1,2)
        # tileServerPanel.addWidget(pg_ts_btn,7,2,1,2)
        # tileServerPanel.addWidget(logout_btn,8,0,1,4)

        tileServerPanel.addWidget(config_btn,0,0)
        tileServerPanel.addWidget(meta_data_btn,0,1)
        tileServerPanel.addWidget(logout_btn,0,2)

        tileServerPanel.addWidget(upl_files, 1, 0, 1, 2)
        tileServerPanel.addWidget(transactional_api_upload_btn, 1, 2)

        tileServerPanel.addWidget(transactional_api_btn, 2, 0)
        tileServerPanel.addWidget(proj_to_postgis, 2, 1)
        tileServerPanel.addWidget(load_proj_from_postgis, 2, 2)

        tileServerPanel.addWidget(data_mbtile_distributon_endp, 3, 0)
        tileServerPanel.addWidget(data_gpkg_distributon_endp, 3, 1)
        tileServerPanel.addWidget(data_style_distributon_endp, 3, 2)

        tileServerPanel.addWidget(data_cached_ms, 4, 0)
        tileServerPanel.addWidget(pg_fs_btn, 4, 1)
        tileServerPanel.addWidget(pg_ts_btn, 4, 2)

        tileServerPanel.addWidget(file_list_api_btn, 5, 0)
        tileServerPanel.addWidget(data_cog_endp, 5, 1)

        tileServerPanel.addWidget(pocketbase_collection_formbuilder_webview_btn,6,0)
        tileServerPanel.addWidget(edge_team_collaboration_webview_btn,6,1)
        tileServerPanel.addWidget(openlayers2d_webview_btn,6,2)
        tileServerPanel.addWidget(terria3d_webview_btn,7,0)
        tileServerPanel.addWidget(discover_webview_btn,7,1)
        tileServerPanel.addWidget(catalog_generator_webview_btn,7,2)
        # webviewVerticalPanel.addWidget(team_collaboration_app_webview_btn)
        # tileServerPanel.addWidget(tileserver_label,0,0)
        #
        #
        #
        #
        #
        # tileServerPanel.addWidget(webview_label,8,0,1,4)


        upload_buttons = [transactional_api_btn,transactional_api_upload_btn,upl_files,proj_to_postgis,load_proj_from_postgis]
        logout_buttons = [logout_btn]
        data_buttons = [
                            pg_fs_btn,
                            pg_ts_btn,
                            data_cog_endp,
                            data_mbtile_distributon_endp,
                            data_gpkg_distributon_endp,
                            data_style_distributon_endp,
                            data_cached_ms,
                            file_list_api_btn
                        ]
        config_buttons = [config_btn,meta_data_btn]
        # Common button styling
        webview_buttons = [
            pocketbase_collection_formbuilder_webview_btn,
            # team_collaboration_app_webview_btn,
            catalog_generator_webview_btn,
            discover_webview_btn,
            terria3d_webview_btn,
            openlayers2d_webview_btn,
            edge_team_collaboration_webview_btn
        ]

        colors = {
            "webview": {"background-color": "#2B2B2B", "color": "#F0F0F0"},
            # Darker shade for the webview background and light text
            "upload": {"background-color": "#1A5276", "color": "#D6EAF8"},  # Muted blue with light blue text for upload
            "logout": {"background-color": "#CB4335", "color": "#F9EBEA"},  # Softer red for logout with pale pink text
            "data": {"background-color": "#D68910", "color": "#FDF2E9"},  # Rich amber for data with light beige text
            "config": {"background-color": "#117A65", "color": "#D5F5E3"}  # Deep teal for config with pastel green text
        }

        for btn in webview_buttons:
            self.setButtonStyle(btn,"webview",colors)
        for btn in data_buttons:
            self.setButtonStyle(btn,"data",colors)
        for btn in upload_buttons:
            self.setButtonStyle(btn,"upload",colors)
        for btn in logout_buttons:
            self.setButtonStyle(btn,"logout",colors)
        for btn in config_buttons:
            self.setButtonStyle(btn,"config",colors)

        middlePanel.addLayout(webviewVerticalPanel)
        middlePanel.addLayout(tileServerPanel)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(topHorizontalPanel)
        layout.addLayout(middlePanel)

        self.setLayout(layout)

        self.config_file = os.path.join(os.path.dirname(__file__),
                                        'configurations.json')  # Load the existing configuration file
    def setButtonStyle(self,btn , type , colors):
        # Button stylesheets for better look
        button_style = """
                        QPushButton {
                            background-color: """+colors[type]["background-color"]+""";  /* Dark slate blue */
                            color: """+colors[type]["color"]+""";  /* Light grayish blue */
                            border: none;
                            border-radius: 10px;
                            padding: 12px 28px;
                            font-size: 15px;
                            font-weight: 500;
                            text-align: center;
                            transition: background-color 0.3s ease, transform 0.2s;
                        }
                        QPushButton:hover {
                            background-color: #34495E;  /* Slightly lighter dark blue on hover */
                            transform: scale(1.05);  /* Slightly enlarge the button on hover */
                        }
                        QPushButton:pressed {
                            background-color: #1A242F;  /* Darker blue on click */
                            transform: scale(0.98);  /* Slightly shrink the button when pressed */
                        }
                                            """
        btn.setStyleSheet(button_style)

    def load_configurations(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
            return config.get('ToPostgisDirect', [])
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading configurations: {e}")
            return None

    def noImplementation(self):
        QMessageBox.warning(self, 'Error', 'COG Tile server not functional!')



    def openConfigurations(self):
        dlg = TSConfigurationsDialog()

        # show the dialog
        # dlg.show()
        # Run the dialog event loop
        result = dlg.exec_()

    def openMetaDataManager(self):
        dialog = MetadataManagerDialog()
        dialog.exec_()

    def uploadStaticFile(self):
        dlg = UploadStaticFileDialog(False)
        result = dlg.exec_()

    def showTransactionalApiUpload(self):
        dlg = UploadStaticFileDialog(True)
        result = dlg.exec_()

    def loadProjFromPostgis(self):
        dlg = LoadProjectFromPostgis()
        result = dlg.exec_()

    def projToPostgis(self):
        dialog = ProjectToPostgis(self.configurations)
        result = dialog.exec_()

        if result:
            try:
                if not dialog.new_connection_checkbox.isChecked():
                    dialog.selected_connection = dialog.connection_dropdown.currentData()
                    if not dialog.selected_connection:
                        QMessageBox.warning(self, 'No Connection Selected', 'Please select a database connection.')
                        return

                    host = dialog.selected_connection['host']
                    port = dialog.selected_connection['port']
                    database = dialog.selected_connection['database']
                    user = dialog.selected_connection['user']
                    password = dialog.selected_connection['password']

                else:
                    # Get connection parameters from dialog
                    host = dialog.host_input.text()
                    port = dialog.port_input.text()
                    database = dialog.database_input.text()
                    user = dialog.user_input.text()
                    password = dialog.password_input.text()

                # Connect to PostgreSQL
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )

                # Save project to database
                if self.save_project_to_database(conn):

                    QMessageBox.information(None, "Success", "Project saved to PostGIS successfully!")


            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save project: {str(e)}")

    def save_project_to_database(self, conn):
        # Get current project
        project = QgsProject.instance()
        if project.fileName() == "":
            QMessageBox.critical(None, "Error", f"You must save the project file before loading into database!")
            return False
        # Create project data dictionary
        project_data = {
            'project_name': project.fileName(),
            'layers': self.get_layers_info(),
            'extent': self.get_project_extent(),
            'crs': project.crs().authid(),
            'title': project.title(),
            'creation_date': project.lastSaveDateTime().toString(),
            'file_path':project.absoluteFilePath()
        }

        # Convert to JSON
        project_json = json.dumps(project_data)

        # Create cursor
        cur = conn.cursor()

        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qgis_projects (
                id SERIAL PRIMARY KEY,
                project_name TEXT,
                project_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert project data
        cur.execute("""
            INSERT INTO qgis_projects (project_name, project_data)
            VALUES (%s, %s);
        """, (project.fileName(), project_json))

        # Commit transaction
        conn.commit()

        # Close cursor
        cur.close()
        return True

    def get_layers_info(self):
        layers = []
        for layer in QgsProject.instance().mapLayers().values():
            layer_info = {
                'name': layer.name(),
                'type': layer.type(),
                'source': layer.source(),
                'provider': layer.providerType(),
                'crs': layer.crs().authid()
            }
            layers.append(layer_info)
        return layers

    def get_project_extent(self):
        extent = self.iface.mapCanvas().extent()
        return {
            'xmin': extent.xMinimum(),
            'ymin': extent.yMinimum(),
            'xmax': extent.xMaximum(),
            'ymax': extent.yMaximum()
        }

    def openWebView(self , title , webviewType):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}

        url_template = config.get(webviewType)
        if url_template:
            tile_server_url = config.get("TileServerUrl")
            tile_server_url = tile_server_url.rstrip("/")

            tile_server_port = config.get("TileServerPort")
            url_template = url_template.replace("tile_server_url",tile_server_url+":"+tile_server_port)
            dlg = OpenWebView(title , url_template)
            result = dlg.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Url not defined!')

    def pgFeatureServer(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}

        pgFsUrl = config.get("OGCApiFeature", "")
        pgFsUrl = pgFsUrl + "/collections.json"
        if pgFsUrl == "":
            QMessageBox.warning(self, 'Error', 'Dynamic Vector Tiles url not defined! You can set this in configurations.')
            return

        dlg = PGFeatureServerDialog(pgFsUrl)
        result = dlg.exec_()

    def pgTileServer(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}
        pgTsUrl = config.get("DynamicVectorTiles", "")
        pgTsUrl = pgTsUrl + "/index.json"
        if pgTsUrl == "":
            QMessageBox.warning(self, 'Error', 'OGC Feature Api url not defined! You can set this in configurations.')
            return
        dlg = PGTileServerDialog(pgTsUrl)
        result = dlg.exec_()

    def showDataDistribution(self , configKey):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}
        url_template = config.get(configKey)
        if url_template:
            tile_server_url = config.get("TileServerUrl")
            tile_server_url = tile_server_url.rstrip("/")

            tile_server_port = config.get("TileServerPort")
            url_template = url_template.replace("tile_server_url", tile_server_url + ":" + tile_server_port)
            print(url_template)
            dlg = DataDistributionDialog(configKey, url_template)
            result = dlg.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Url not defined!')

    def showCachedMapTiles(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}

        url_template = config.get("CachedMapTiles")
        if url_template:
            tile_server_url = config.get("TileServerUrl")
            tile_server_url = tile_server_url.rstrip("/")

            tile_server_port = config.get("TileServerPort")
            url_template = url_template.replace("tile_server_url", tile_server_url + ":" + tile_server_port)

            dlg = DataDistributionDialog("cached_map_tiles", url_template)
            result = dlg.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Url not defined!')

    def showTransactionalApi(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}

        tile_server_url = config.get("TileServerUrl")
        tile_server_port = config.get("TileServerPort")
        if tile_server_url and tile_server_port:
            tile_server_url = tile_server_url.rstrip("/")
            url_template = urljoin(f"{tile_server_url}:{tile_server_port}", "filelist")
            dump_url = urljoin(f"{tile_server_url}:{tile_server_port}", "dump/pg")
            dlg = DataDistributionDialog("transactional_api", url_template,dump_url)
            result = dlg.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Url not defined!')


    def logout(self):
        self.loginDialog.logout()
        self.accept()


