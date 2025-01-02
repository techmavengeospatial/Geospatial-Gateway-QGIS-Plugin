import json
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, \
    QComboBox
import requests

from ..DatabaseConnectionDialog import DatabaseConnectionDialog


class DatabaseConnectionDropdownWithAddNew(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Plugin Configurations')
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configurations.json')
        self.databaseDlg = DatabaseConnectionDialog()

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