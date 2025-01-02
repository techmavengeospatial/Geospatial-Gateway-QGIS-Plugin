import os
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox
import psycopg2
import json

from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError


class DatabaseConnectionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(DatabaseConnectionDialog, self).__init__(parent)

        self.setWindowTitle("Database Connection Configuration")

        # SSH checkbox
        self.ssh_checkbox = QCheckBox("Is SSH Connection")
        self.ssh_checkbox.stateChanged.connect(self.toggle_ssh_fields)

        # SSH fields
        self.ssh_host_label = QLabel("SSH Host:")
        self.ssh_host_input = QLineEdit()
        self.ssh_port_label = QLabel("SSH Port:")
        self.ssh_port_input = QLineEdit()
        self.ssh_user_label = QLabel("SSH Username:")
        self.ssh_user_input = QLineEdit()
        self.ssh_password_label = QLabel("SSH Password:")
        self.ssh_password_input = QLineEdit()
        self.ssh_password_input.setEchoMode(QLineEdit.Password)

        # Database fields
        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit()
        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        self.database_label = QLabel("Database:")
        self.database_input = QLineEdit()
        self.user_label = QLabel("User:")
        self.user_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.project_label = QLabel("Project Name:")
        self.project_input = QLineEdit()

        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.save_configuration)

        layout = QVBoxLayout()
        layout.addWidget(self.ssh_checkbox)

        layout.addWidget(self.ssh_host_label)
        layout.addWidget(self.ssh_host_input)
        layout.addWidget(self.ssh_port_label)
        layout.addWidget(self.ssh_port_input)
        layout.addWidget(self.ssh_user_label)
        layout.addWidget(self.ssh_user_input)
        layout.addWidget(self.ssh_password_label)
        layout.addWidget(self.ssh_password_input)

        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.database_label)
        layout.addWidget(self.database_input)
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.project_label)
        layout.addWidget(self.project_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Initially disable SSH fields
        self.toggle_ssh_fields()

    def toggle_ssh_fields(self):
        """Toggle SSH-related fields based on the checkbox state."""
        is_ssh = self.ssh_checkbox.isChecked()
        self.ssh_host_label.setEnabled(is_ssh)
        self.ssh_host_input.setEnabled(is_ssh)
        self.ssh_port_label.setEnabled(is_ssh)
        self.ssh_port_input.setEnabled(is_ssh)
        self.ssh_user_label.setEnabled(is_ssh)
        self.ssh_user_input.setEnabled(is_ssh)
        self.ssh_password_label.setEnabled(is_ssh)
        self.ssh_password_input.setEnabled(is_ssh)

    def save_configuration(self):
        host = self.host_input.text()
        port = self.port_input.text()
        database = self.database_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        project_name = self.project_input.text()

        is_ssh = self.ssh_checkbox.isChecked()
        ssh_host = self.ssh_host_input.text() if is_ssh else None
        ssh_port = self.ssh_port_input.text() if is_ssh else None
        ssh_user = self.ssh_user_input.text() if is_ssh else None
        ssh_password = self.ssh_password_input.text() if is_ssh else None

        # Check for empty fields
        if not all([host, port, database, user, password, project_name]) or (
                is_ssh and not all([ssh_host, ssh_port, ssh_user, ssh_password])):
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        # Test PostgreSQL connection
        try:
            if is_ssh:
                with SSHTunnelForwarder(
                        (ssh_host, int(ssh_port)),
                        ssh_username=ssh_user,
                        ssh_password=ssh_password,
                        remote_bind_address=(host, int(port))
                ) as tunnel:
                    conn = psycopg2.connect(
                        host='127.0.0.1',  # Localhost because of the SSH tunnel
                        port=tunnel.local_bind_port,
                        database=database,
                        user=user,
                        password=password
                    )
                    conn.close()
            else:
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                conn.close()
        except (psycopg2.Error, BaseSSHTunnelForwarderError) as e:
            QMessageBox.warning(self, "Error", f"Failed to connect to PostgreSQL:\n{str(e)}")
            return

        # Get the path to the script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(script_dir, 'configurations.json')

        # Load existing configurations
        try:
            with open(config_path, 'r') as config_file:
                config_data = json.load(config_file)
        except FileNotFoundError:
            config_data = {}

        # Select the appropriate key for saving
        config_key = "ToPostgisSSH" if is_ssh else "ToPostgisDirect"
        db_config = config_data.get(config_key, [])

        # Check if the connection already exists
        for connection in db_config:
            if connection["host"] == host and connection["port"] == port \
                    and connection["database"] == database and connection["user"] == user:
                QMessageBox.warning(self, "Warning", "Connection already exists in the configuration.")
                return
            elif connection["project_name"] == project_name:
                QMessageBox.warning(self, "Warning", "Project name already exists in the configuration.")
                return

        # Append new connection
        new_connection = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "project_name": project_name
        }

        if is_ssh:
            new_connection.update({
                "ssh_host": ssh_host,
                "ssh_port": ssh_port,
                "ssh_user": ssh_user,
                "ssh_password": ssh_password
            })

        db_config.append(new_connection)
        config_data[config_key] = db_config

        # Save updated configurations with proper indentation
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)

        QMessageBox.information(self, "Success", "Configuration saved successfully.")
        self.accept()

    # End of the class DatabaseConnectionDialog