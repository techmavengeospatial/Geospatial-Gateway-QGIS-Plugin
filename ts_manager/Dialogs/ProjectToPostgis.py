from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QPushButton, QComboBox, QCheckBox, QLabel, QMessageBox, QLineEdit


class ProjectToPostgis(QDialog):
    def __init__(self, configurations):
        super().__init__()
        self.configurations = configurations
        self.setWindowTitle("PostGIS Connection")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Dropdown for existing connections
        self.connection_dropdown = QComboBox(self)
        self.populate_connections()
        layout.addWidget(QLabel('Select Database Connection:'))
        layout.addWidget(self.connection_dropdown)



        # New Connection checkbox
        self.new_connection_checkbox = QCheckBox("New Connection", self)
        self.new_connection_checkbox.stateChanged.connect(self.toggle_connection_fields)
        layout.addWidget(self.new_connection_checkbox)


        # Host input
        layout.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        layout.addWidget(self.host_input)

        # Port input
        layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setText("5432")
        layout.addWidget(self.port_input)

        # Database input
        layout.addWidget(QLabel("Database:"))
        self.database_input = QLineEdit()
        layout.addWidget(self.database_input)

        # User input
        layout.addWidget(QLabel("User:"))
        self.user_input = QLineEdit()
        layout.addWidget(self.user_input)

        # Password input
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Connect button
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.accept)
        layout.addWidget(connect_button)

        self.setLayout(layout)

        # Initially disable the connection fields
        self.toggle_connection_fields()

    def populate_connections(self):
        for connection in self.configurations:
            self.connection_dropdown.addItem(connection.get('project_name'), connection)

    def toggle_connection_fields(self):
        # Enable or disable the input fields based on the checkbox state
        is_new_connection = self.new_connection_checkbox.isChecked()
        # self.project_name_input.setEnabled(is_new_connection)  # Enable the Project Name input for new connections
        self.host_input.setEnabled(is_new_connection)
        self.port_input.setEnabled(is_new_connection)
        self.database_input.setEnabled(is_new_connection)
        self.user_input.setEnabled(is_new_connection)
        self.password_input.setEnabled(is_new_connection)

