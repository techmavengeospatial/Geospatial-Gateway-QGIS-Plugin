import json
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, \
    QTableWidget, QTableWidgetItem
import requests
import psycopg2  # For PostgreSQL connection
from qgis._core import QgsProject

from ..DatabaseConnectionDialog import DatabaseConnectionDialog


class LoadProjectFromPostgis(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Load Project')
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configurations.json')
        self.databaseDlg = DatabaseConnectionDialog()
        self.current_connection = None  # To hold the selected connection's details
        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout()
        # Grid Layout for Two-Column Input Fields
        grid_layout = QGridLayout()
        # Add rows for each input field (left and right columns)
        self.connection_dropdown = QComboBox()
        grid_layout.addWidget(QLabel('PostGIS Connections:'), 0, 0)
        grid_layout.addWidget(self.connection_dropdown, 0, 1)
        add_button = QPushButton("Add New")
        add_button.clicked.connect(self.add_new_connection)
        grid_layout.addWidget(add_button, 0, 2)

        # Add the grid layout to the main layout
        main_layout.addLayout(grid_layout)

        # Add Projects table
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(2)
        self.project_table.setHorizontalHeaderLabels(["Project Name", "Load Project"])
        main_layout.addWidget(self.project_table)

        # Add Load Project Button
        load_button = QPushButton("Load Selected Project")
        load_button.clicked.connect(self.load_selected_project)
        main_layout.addWidget(load_button)

        self.setLayout(main_layout)
        self.loadConnections()

    def loadConnections(self):
        config_data = self.load_database_configurations()
        postgres_configs = config_data.get("ToPostgisDirect", [])
        self.connection_dropdown.clear()
        for config in postgres_configs:
            self.connection_dropdown.addItem(config.get("project_name", "Unnamed"))

        # Connect a change event to load projects based on the selected connection
        self.connection_dropdown.currentIndexChanged.connect(self.on_connection_change)

    def load_database_configurations(self):
        with open(self.config_file, 'r') as config_file:
            return json.load(config_file)

    def on_connection_change(self):
        selected_connection_name = self.connection_dropdown.currentText()
        self.current_connection = self.get_connection_details(selected_connection_name)
        if self.current_connection:
            self.load_projects_from_database()

    def get_connection_details(self, connection_name):
        config_data = self.load_database_configurations()
        postgres_configs = config_data.get("ToPostgisDirect", [])
        for config in postgres_configs:
            if config.get("project_name") == connection_name:
                return config
        return None

    def load_projects_from_database(self):
        if not self.current_connection:
            return

        # Connect to the selected PostGIS database and fetch project names
        try:
            conn = psycopg2.connect(
                host=self.current_connection['host'],
                port=self.current_connection['port'],
                dbname=self.current_connection['database'],
                user=self.current_connection['user'],
                password=self.current_connection['password']
            )
            cur = conn.cursor()
            cur.execute("SELECT project_name FROM qgis_projects;")
            projects = cur.fetchall()

            # Clear the existing projects in the table
            self.project_table.setRowCount(0)

            # Add each project to the table
            for row_idx, project in enumerate(projects):
                self.project_table.insertRow(row_idx)
                self.project_table.setItem(row_idx, 0, QTableWidgetItem(project[0]))  # Project Name
                load_button_item = QPushButton("Load")
                load_button_item.clicked.connect(lambda _, project_name=project[0]: self.load_project(project_name))
                self.project_table.setCellWidget(row_idx, 1, load_button_item)

            cur.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load projects: {str(e)}")

    def load_selected_project(self):
        # Get the selected project name from the table
        selected_row = self.project_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a project to load.")
            return

        project_name = self.project_table.item(selected_row, 0).text()
        self.load_project(project_name)

    def load_project(self, project_name):
        # Logic to load the selected project into QGIS
        try:
            # For example, you can fetch the project data from the database and load it
            conn = psycopg2.connect(
                host=self.current_connection['host'],
                port=self.current_connection['port'],
                dbname=self.current_connection['database'],
                user=self.current_connection['user'],
                password=self.current_connection['password']
            )
            cur = conn.cursor()
            cur.execute("SELECT project_data FROM qgis_projects WHERE project_name = %s;", (project_name,))
            project_data = cur.fetchone()
            if project_data:
                # Deserialize the JSON data

                project_info = project_data[0]
                # Here you can use QGIS APIs to load the project, e.g., QgsProject.instance().read()
                # For now, we'll just print it
                # Add your QGIS project loading code here
                QgsProject.instance().read(project_info['file_path'])

            cur.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load the project: {str(e)}")

    def add_new_connection(self):
        self.databaseDlg.exec_()
        self.loadConnections()
