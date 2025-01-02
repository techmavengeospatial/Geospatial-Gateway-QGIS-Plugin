import base64
import time
from enum import verify

import requests
from qgis.PyQt.QtWidgets import QComboBox,QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QFormLayout, QMessageBox, QProgressBar,QProgressDialog
# from qgis.PyQt.QtCore import Qt,QThread, pyqtSignal
from qgis.PyQt.QtGui import QFontMetrics
import json
import os

from pathlib import Path
from tqdm import tqdm


from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from PyQt5.QtCore import Qt, QThread, pyqtSignal




import math

from qgis._core import QgsMessageLog, Qgis


class UploadStaticFileDialog(QDialog):
    lastSelectedType = None
    def __init__(self, transactionalApi,parent=None):
        super().__init__(parent)
        self.transactionalApi = transactionalApi

        self.setWindowTitle('Upload Static File')
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'configurations.json')# Load the existing configuration file
        layout = QVBoxLayout()
        self.fileTypes = ["mbtile", "gpkg", "style", "other"]
        self.fileTypeForBrowse = {"mbtile":"Mbtiles (*.mbtiles)", "cog":"GeoTIFF Files (*.tiff *.tif)", "files":"All Files (*)", "3dtiles":"3D Tiles (*.3dtiles)", "catlog":"All Files (*)", "gpkg":"Geopackage (*.gpkg)", "geojson": "GeoJSON (*.geojson *.json)", "styles":"Style (*.json)", "other":"All Files (*)"}
        form_layout = QFormLayout()

        # Load configuration and set StaticFiles URL
        if self.transactionalApi:
            self.static_files_url = self.load_configuration("TransactionalAPI_Upload")
            self.static_files_label = QLabel("Transactional Api URL:")
        else:
            self.static_files_url = self.load_configuration("UploadUrl")
            self.static_files_label = QLabel("Static Files URL:")
        self.static_files_input = QLineEdit(self.static_files_url)
        self.adjust_url_input_width(self.static_files_input)

        self.static_files_input.setReadOnly(True)
        
        self.file_label = QLabel("File:")
        self.file_input = QLineEdit()
        if not self.transactionalApi:
            self.file_type_dropdown = QComboBox(self)
            self.file_type_dropdown.currentIndexChanged.connect(self.inputTypeChanged)


        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_file)
        
        self.company_label = QLabel("Company:")
        # self.company_input = QLineEdit(self.company_name)
        
        form_layout.addRow(self.static_files_label, self.static_files_input)
        form_layout.addRow(self.file_label, self.file_input)
        form_layout.addRow('', self.file_button)
        if not self.transactionalApi:
            form_layout.addRow(QLabel("File type"),self.file_type_dropdown)
            self.fill_file_type_dropdown()
        # form_layout.addRow(self.company_label, self.company_input)
        layout.addLayout(form_layout)
        
        self.upload_button = QPushButton('Upload')
        self.upload_button.clicked.connect(self.upload_data)
        layout.addWidget(self.upload_button)
        
        self.setLayout(layout)



    def inputTypeChanged(self):
        selectedType = self.file_type_dropdown.currentText()
        if self.lastSelectedType is None:
            self.static_files_input.setText(self.static_files_input.text().format(type=selectedType))
            self.lastSelectedType = selectedType
        else:
            self.static_files_input.setText(self.static_files_input.text().replace(self.lastSelectedType , selectedType))
            self.lastSelectedType = selectedType

    def adjust_url_input_width(self, input_to_adjust):
        text = input_to_adjust.text()
        font_metrics = QFontMetrics(input_to_adjust.font())
        text_width = font_metrics.horizontalAdvance(text)

        # Add some padding to the width
        new_width = text_width + 10

        # Set the width of the QLineEdit
        input_to_adjust.setFixedWidth(new_width)

    def fill_file_type_dropdown(self):
        for type in self.fileTypes:
            self.file_type_dropdown.addItem(type)

    def load_configuration(self, uploadType):
        try:
            with open(self.config_path, 'r') as config_file:
                config = json.load(config_file)
                static_files_url = config.get(uploadType, 'URL not found')
                # upload_url = config.get('UploadURL', 'https://gismapserver.com/upload')
                return static_files_url
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'configurations.json file not found.')
            return 'URL not found'
        except json.JSONDecodeError:
            QMessageBox.critical(self, 'Error', 'Error decoding configurations.json file.')
            return 'URL not found'

    def browse_file(self):
        file_path = None
        if not self.transactionalApi:
            fileType = self.file_type_dropdown.currentText()
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.fileTypeForBrowse[fileType], options=options)
        else:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)",
                                                       options=options)
        if file_path:
            self.file_input.setText(file_path)

    # File upload fully working
    # def upload_data(self):
    #     file_path = self.file_input.text()
    #     if self.static_files_url == "URL not found":
    #         QMessageBox.warning(self, 'Input Error', 'URL is required!')
    #         return
    #     if not all([file_path, self.static_files_url]):
    #         QMessageBox.warning(self, 'Input Error', 'Both fields are mandatory.')
    #         return
    #
    #     current_url = self.static_files_input.text()
    #
    #     # Check if the file exists
    #     if not os.path.isfile(file_path):
    #         QMessageBox.warning(self, 'Input Error', 'File does not exist!')
    #         return
    #
    #     path = Path(file_path)
    #     total_size = path.stat().st_size
    #     filename = path.name
    #     fields = {}
    #
    #     # Create a progress dialog
    #     progress_dialog = QProgressDialog("Uploading file...", "Cancel", 0, total_size, self)
    #     progress_dialog.setWindowTitle("File Upload Progress")
    #     progress_dialog.setValue(0)
    #     progress_dialog.setCancelButtonText("Cancel")
    #     progress_dialog.setModal(True)
    #     progress_dialog.show()
    #
    #     try:
    #         with open(file_path, "rb") as f:
    #             fields["file"] = (filename, f)
    #             encoder = MultipartEncoder(fields=fields)
    #             monitor = MultipartEncoderMonitor(
    #                 encoder, lambda monitor: progress_dialog.setValue(monitor.bytes_read)
    #             )
    #
    #             headers = {"Content-Type": monitor.content_type}
    #             response = requests.post(current_url, data=monitor, headers=headers, verify=False)
    #
    #             # Check the response status
    #             if response.status_code == 200:
    #                 QMessageBox.information(self, "Success", "File uploaded successfully!")
    #             else:
    #                 QMessageBox.warning(self, "Upload Failed", f"Failed to upload file: {response.text}")
    #
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    #     finally:
    #         progress_dialog.close()
    #
    #     # Close the progress dialog if it is still open
    #     if progress_dialog.isVisible():
    #         progress_dialog.close()



    def upload_data(self):
        file_path = self.file_input.text()
        if self.static_files_url == "URL not found":
            QMessageBox.warning(self, 'Input Error', 'URL is required!')
            return
        if not all([file_path, self.static_files_url]):
            QMessageBox.warning(self, 'Input Error', 'Both fields are mandatory.')
            return

        current_url = self.static_files_input.text()

        # Check if the file exists
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, 'Input Error', 'File does not exist!')
            return

        path = Path(file_path)
        total_size = path.stat().st_size
        filename = path.name
        fields = {}

        # Create a progress dialog
        progress_dialog = QProgressDialog("Uploading file...", "Cancel", 0, total_size, self)
        progress_dialog.setWindowTitle("File Upload Progress")
        progress_dialog.setValue(0)
        progress_dialog.setCancelButtonText("Cancel")
        progress_dialog.setModal(True)
        progress_dialog.show()

        # Variables for speed calculation
        start_time = time.time()
        last_bytes_read = 0

        try:
            with open(file_path, "rb") as f:
                fields["File"] = (filename, f)
                # fields["Company"] = "TMG"
                encoder = MultipartEncoder(fields=fields)
                monitor = MultipartEncoderMonitor(
                    encoder, lambda monitor: self.update_progress(progress_dialog, monitor, start_time, last_bytes_read)
                )

                headers = {"Content-Type": monitor.content_type}
                response = requests.post(current_url, data=monitor, headers=headers, verify=False)

                # Check the response status
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "File uploaded successfully!")
                else:
                    QMessageBox.warning(self, "Upload Failed", f"Failed to upload file: {response.text}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            progress_dialog.close()

    def update_progress(self, progress_dialog, monitor, start_time, last_bytes_read):
        current_bytes_read = monitor.bytes_read
        progress_dialog.setValue(current_bytes_read)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        if elapsed_time > 0:
            # Calculate upload speed in bytes per second
            upload_speed = (current_bytes_read - last_bytes_read) / elapsed_time
            last_bytes_read = current_bytes_read

            # Convert speed to KB/s or MB/s
            if upload_speed >= 1024 * 1024:  # 1 MB/s
                speed_str = f"{upload_speed / (1024 * 1024):.2f} MB/s"
            elif upload_speed >= 1024:  # 1 KB/s
                speed_str = f"{upload_speed / 1024:.2f} KB/s"
            else:
                speed_str = f"{upload_speed:.2f} Bytes/s"

            progress_dialog.setLabelText(f"Uploading file... Speed: {speed_str}")

        return last_bytes_read