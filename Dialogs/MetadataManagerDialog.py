import psycopg2
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                                 QLabel, QPushButton, QComboBox, QTextEdit)
from qgis.PyQt.QtCore import Qt
import json
import os


class MetadataManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metadata Manager")
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                        'configurations.json')  # Load the existing configuration file

        self.setup_ui()
        self.loadConnections()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create form fields
        self.name_edit = QLineEdit()
        self.table_name_edit = QLineEdit()

        self.geom_type_combo = QComboBox()
        self.geom_type_combo.addItems(['Point', 'LineString', 'Polygon', 'MultiPoint',
                                       'MultiLineString', 'MultiPolygon'])

        self.bbox_edit = QLineEdit()
        self.srs_edit = QLineEdit()
        self.project_edit = QLineEdit()
        self.tags_edit = QLineEdit()
        self.labels_edit = QLineEdit()
        self.metadata_text = QTextEdit()

        # Add fields to layout
        form_layout = QVBoxLayout()

        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_edit)

        form_layout.addWidget(QLabel("Table Name:"))
        form_layout.addWidget(self.table_name_edit)

        form_layout.addWidget(QLabel("Geometry Type:"))
        form_layout.addWidget(self.geom_type_combo)

        form_layout.addWidget(QLabel("Bounding Box:"))
        form_layout.addWidget(self.bbox_edit)

        form_layout.addWidget(QLabel("SRS:"))
        form_layout.addWidget(self.srs_edit)

        form_layout.addWidget(QLabel("Project:"))
        form_layout.addWidget(self.project_edit)

        form_layout.addWidget(QLabel("Tags:"))
        form_layout.addWidget(self.tags_edit)

        form_layout.addWidget(QLabel("Labels:"))
        form_layout.addWidget(self.labels_edit)

        form_layout.addWidget(QLabel("Metadata:"))
        form_layout.addWidget(self.metadata_text)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_metadata)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Create connection dropdown
        self.connection_dropdown = QComboBox()
        self.connection_dropdown.currentTextChanged.connect(self.on_connection_change)

        # Add connection dropdown to the form layout
        form_layout.addWidget(QLabel("PostGIS Connection:"))
        form_layout.addWidget(self.connection_dropdown)

        # Add all layouts to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def loadConnections(self):
        config_data = self.load_database_configurations()
        postgres_configs = config_data.get("ToPostgisDirect", [])
        self.connection_dropdown.clear()
        for config in postgres_configs:
            self.connection_dropdown.addItem(config.get("project_name", "Unnamed"))

    def load_database_configurations(self):
        with open(self.config_file, 'r') as config_file:
            return json.load(config_file)

    def on_connection_change(self, connection_name):
        """Update the form when the connection is changed."""
        if not connection_name:
            self.clear_form()
            return

        # Fetch the selected connection details from the configuration
        config_data = self.load_database_configurations()
        selected_config = None
        for config in config_data.get("ToPostgisDirect", []):
            if config.get("project_name") == connection_name:
                selected_config = config
                break
        if selected_config is None:
            self.clear_form()
            return

        # Get connection details
        host = selected_config.get("host")
        port = selected_config.get("port", 5432)
        dbname = selected_config.get("database")
        user = selected_config.get("user")
        password = selected_config.get("password")

        # Connect to the selected PostGIS database
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            cursor = conn.cursor()

            # Check if the 'data_contents' table exists
            cursor.execute("""SELECT EXISTS (
                                  SELECT 1
                                  FROM information_schema.tables
                                  WHERE table_name = 'data_contents'
                              );""")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                self.clear_form()
                return

            # Fetch the first row from the 'data_contents' table (assuming only one row)
            cursor.execute("SELECT * FROM data_contents LIMIT 1")
            record = cursor.fetchone()

            if record:
                # Pre-fill form fields with data from the database
                self.name_edit.setText(record[0])  # NameI
                self.table_name_edit.setText(record[2])  # Table_name
                self.geom_type_combo.setCurrentText(record[3])  # Geom_type
                self.bbox_edit.setText(record[4])  # BBOX
                self.srs_edit.setText(record[5])  # SRS
                self.project_edit.setText(record[6])  # PROJECT
                self.tags_edit.setText(record[7])  # TAGS
                self.labels_edit.setText(record[8])  # LABELS
                self.metadata_text.setPlainText(record[9])  # Metadata
            else:
                self.clear_form()

            conn.commit()

        except psycopg2.Error as e:
            self.show_error(f"Database error: {str(e)}")
        finally:
            if conn:
                conn.close()

    def clear_form(self):
        """Clear all input fields."""
        self.name_edit.clear()
        self.table_name_edit.clear()
        self.geom_type_combo.setCurrentIndex(0)
        self.bbox_edit.clear()
        self.srs_edit.clear()
        self.project_edit.clear()
        self.tags_edit.clear()
        self.labels_edit.clear()
        self.metadata_text.clear()

    def save_metadata(self):
        # Collect form data
        data = {
            'NameI': self.name_edit.text(),
            'Table_name': self.table_name_edit.text(),
            'Geom_type': self.geom_type_combo.currentText(),
            'BBOX': self.bbox_edit.text(),
            'SRS': self.srs_edit.text(),
            'PROJECT': self.project_edit.text(),
            'TAGS': self.tags_edit.text(),
            'LABELS': self.labels_edit.text(),
            'Metadata': self.metadata_text.toPlainText()
        }

        # Validate required fields
        if not data['NameI']:
            self.show_error("Name is required!")
            return

        connection_name = self.connection_dropdown.currentText()
        if not connection_name:
            self.show_error("Please select a PostGIS connection.")
            return

        # Fetch the selected connection details from the configuration
        config_data = self.load_database_configurations()
        selected_config = None
        for config in config_data.get("ToPostgisDirect", []):
            if config.get("project_name") == connection_name:
                selected_config = config
                break

        if selected_config is None:
            self.show_error(f"Connection '{connection_name}' not found.")
            return

        # Get connection details
        host = selected_config.get("host")
        port = selected_config.get("port", 5432)
        dbname = selected_config.get("database")
        user = selected_config.get("user")
        password = selected_config.get("password")

        # Connect to the selected PostGIS database
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            cursor = conn.cursor()

            # Check if the 'data_contents' table exists, if not create it
            cursor.execute("""SELECT EXISTS (
                                  SELECT 1
                                  FROM information_schema.tables
                                  WHERE table_name = 'data_contents'
                              );""")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.execute('''CREATE TABLE data_contents (
                                  NameI TEXT,
                                  Table_name TEXT,
                                  Geom_type TEXT,
                                  BBOX TEXT,
                                  SRS TEXT,
                                  PROJECT TEXT,
                                  TAGS TEXT,
                                  LABELS TEXT,
                                  Metadata TEXT
                              );''')

            # Update or Insert the single row in the 'data_contents' table
            cursor.execute('''UPDATE data_contents
                              SET NameI=%s, Table_name=%s, Geom_type=%s, BBOX=%s, SRS=%s,
                                  PROJECT=%s, TAGS=%s, LABELS=%s, Metadata=%s
                              WHERE true''',
                           (data['NameI'], data['Table_name'], data['Geom_type'], data['BBOX'],
                            data['SRS'], data['PROJECT'], data['TAGS'], data['LABELS'],
                            data['Metadata']))

            conn.commit()
            self.accept()

        except psycopg2.Error as e:
            self.show_error(f"Database error: {str(e)}")
        finally:
            if conn:
                conn.close()

    def show_error(self, message):
        """Display an error message."""
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        error_dialog.setModal(True)
        error_layout = QVBoxLayout()
        error_layout.addWidget(QLabel(message))
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(error_dialog.accept)
        error_layout.addWidget(ok_button)
        error_dialog.setLayout(error_layout)
        error_dialog.exec_()
