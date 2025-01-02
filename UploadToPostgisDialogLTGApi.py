from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics

import requests
import os 
import json 

class UploadToPostgisDialogLTGApi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Upload to PostGIS')
        
        self.config_file = os.path.join(os.path.dirname(__file__),'configurations.json')# Load the existing configuration file
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}


        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.url_label = QLabel("URL:")
        self.url_input = QLineEdit(config.get("ToPostgisApi",""))

        self.file_label = QLabel("File:")
        self.file_input = QLineEdit()
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_file)
        
        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit()
        
        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.database_label = QLabel("Database:")
        self.database_input = QLineEdit()
        
        self.schema_label = QLabel("Schema:")
        self.schema_input = QLineEdit()
        
        self.tablename_label = QLabel("Table Name:")
        self.tablename_input = QLineEdit()
        
        form_layout.addRow(self.url_label,self.url_input)
        form_layout.addRow(self.file_label, self.file_input)
        form_layout.addRow('', self.file_button)
        form_layout.addRow(self.host_label, self.host_input)
        form_layout.addRow(self.port_label, self.port_input)
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.database_label, self.database_input)
        form_layout.addRow(self.schema_label, self.schema_input)
        form_layout.addRow(self.tablename_label, self.tablename_input)
        
        layout.addLayout(form_layout)
        
        self.upload_button = QPushButton('Upload')
        self.upload_button.clicked.connect(self.upload_data)
        layout.addWidget(self.upload_button)
        
        self.setLayout(layout)

        self.adjust_url_input_width(self.url_input)
    
    def adjust_url_input_width(self, input_to_adjust):
        text = input_to_adjust.text()
        font_metrics = QFontMetrics(input_to_adjust.font())
        text_width = font_metrics.horizontalAdvance(text)
        
        # Add some padding to the width
        new_width = text_width + 10
        
        # Set the width of the QLineEdit
        input_to_adjust.setFixedWidth(new_width)

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "GeoJSON Files (*.geojson);;JSON Files (*.json);;GPKG Files (*.gpkg)", options=options)
        if file_path:
            self.file_input.setText(file_path)
    
    def upload_data(self):
        file_path = self.file_input.text()
        host = self.host_input.text()
        port = self.port_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        database = self.database_input.text()
        schema = self.schema_input.text()
        tablename = self.tablename_input.text()
        
        if not all([file_path, host, port, username, password, database, schema, tablename]):
            QMessageBox.warning(self, 'Input Error', 'All fields are mandatory.')
            return
        
        url = self.url_input.text()  # Replace with actual URL
        files = {'file': open(file_path, 'rb')}
        data = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database,
            'schema': schema,
            'tablename': tablename
        }
        
        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            QMessageBox.information(self, 'Success', 'File uploaded successfully.')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', f'Failed to upload file: {e}')

    def import_shapefile_to_postgis(self,shapefile_path, table_name):
        host=self.selected_connection['host']
        port=self.selected_connection['port']
        database=self.selected_connection['database']
        user=self.selected_connection['user']
        password=self.selected_connection['password']
        table_name = table_name.replace(" ","_").replace("-" , "_").lower()
        # connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        con_string = f"dbname='{database}' host='{host}' port='{port}' user='{user}' password='{password}' key=id table='{table_name}'" + " (geom)"

        layer = QgsVectorLayer(shapefile_path, table_name, "ogr")
        self.execute_sql_sa(f'DROP TABLE IF EXISTS "{table_name}"')
        # print(layer.sourceCrs() )
        err = QgsVectorLayerExporter.exportLayer(layer, con_string, 'postgres', QgsCoordinateReferenceSystem(layer.sourceCrs()), False)

    def execute_sql_sa(self, sql):
        # Connect to PostgreSQL using psycopg2
        conn = psycopg2.connect(
            host=self.selected_connection['host'],
            port=self.selected_connection['port'],
            database=self.selected_connection['database'],
            user=self.selected_connection['user'],
            password=self.selected_connection['password']
        )
        # print(config_data['user'])
        # Execute SQL statements
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()

        # Close the connection
        conn.close()

