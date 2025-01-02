import json
from enum import verify

import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class TransactionApiDialog(QDialog):
    def __init__(self, file_url, dump_url):
        super().__init__()
        self.setWindowTitle('Transaction API Dialog')
        self.file_url = file_url
        self.dump_url = dump_url
        print("dump url")
        print(dump_url)

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout()

        # FileUrl (non-editable, pre-filled)
        file_url_label = QLabel("File URL")
        self.file_url_input = QLineEdit()
        self.file_url_input.setText(self.file_url)
        # self.file_url_input.setReadOnly(True)  # Make it non-editable
        main_layout.addWidget(file_url_label)
        main_layout.addWidget(self.file_url_input)

        # TableName (editable)
        table_name_label = QLabel("Table Name")
        self.table_name_input = QLineEdit()
        main_layout.addWidget(table_name_label)
        main_layout.addWidget(self.table_name_input)

        # LayerName (editable)
        layer_name_label = QLabel("Layer Name")
        self.layer_name_input = QLineEdit()
        main_layout.addWidget(layer_name_label)
        main_layout.addWidget(self.layer_name_input)

        # Publish Button
        publish_button = QPushButton("Publish")
        publish_button.clicked.connect(self.publish_data)
        main_layout.addWidget(publish_button)

        self.setLayout(main_layout)

    def publish_data(self):
        # Collect data from inputs
        data = {
            "FileURL": self.file_url,  # Use the file_url passed in constructor
            "TableName": self.table_name_input.text(),
            "LayerName": self.layer_name_input.text()
        }
        print(data)
        # Send POST request
        try:
            response = requests.post(self.dump_url, json=data,verify=False)
            response.raise_for_status()  # Check for HTTP request errors
            result = response.text
            QMessageBox.information(self, "Success", f"Response: {json.dumps(result, indent=4)}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Request failed: {str(e)}")
