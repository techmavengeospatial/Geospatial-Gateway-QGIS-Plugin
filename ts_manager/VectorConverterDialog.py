# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorConverterDialog
                                 A QGIS plugin
 The LTG Api plugin for QGIS is a powerful tool that enables users to seamlessly interact with online Live Tech Geo API. With this plugin, users can upload static GIS files, including MBTiles and other static files, for later use. Additionally, it allows for the conversion of vector files into various formats such as shapefile, geojson, kml, and mbtiles, which can then be published to a new table in PostGIS, making them accessible as XYZ tiles. Furthermore, users can upload custom styles to enhance their data visualization. The plugin also provides a convenient way to browse static GIS files hosted on the server and explore pg_featureserv endpoints, making it a comprehensive solution for working with online LTG API in QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-07-11
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Tech Maven Geospatial
        email                : jordan@techmaven.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic, QtWidgets
import requests
from tqdm import tqdm
import os


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'TS_Manager_dialog_base.ui'))


class VectorConverterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(VectorConverterDialog, self).__init__(parent)
        self.setWindowTitle('Vector Conversion Tool')
        
        # Add a heading for vector conversion
        self.heading_label = QtWidgets.QLabel('Vector Conversion', self)
        self.heading_label.setGeometry(10, 10, 200, 30)
        font = self.heading_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.heading_label.setFont(font)
        
        # Add combobox for input format
        self.input_label = QtWidgets.QLabel('Input Format:', self)
        self.input_label.setGeometry(10, 50, 100, 30)
        self.input_combobox = QtWidgets.QComboBox(self)
        self.input_combobox.setGeometry(120, 50, 200, 30)
        
        # Add items with key-value pairs
        input_formats = {
            'Shapefile - zip': 'shp',
            'Mapinfo - zip': 'mapinfo',
            'File GDB - zip': 'gdb',
            'Geopackage - gpkg': 'gpkg',
            'MBTILES - mbtiles': 'mbtiles',
            'GeoJson - geojson': 'geojson',
            'KML - kml': 'kml',
            'Comma Separated File - csv': 'csv',
            'AutoCAD - DXF': 'dxf',
            'MicroStation - DGN': 'dgn'
        }
        
        for text, key in input_formats.items():
            self.input_combobox.addItem(text, key)
        
        # Add combobox for output format
        self.output_label = QtWidgets.QLabel('Output Format:', self)
        self.output_label.setGeometry(10, 90, 100, 30)
        self.output_combobox = QtWidgets.QComboBox(self)
        self.output_combobox.setGeometry(120, 90, 200, 30)
        
        output_formats = {
            'ShapeFile': 'shp',
            'MapInfo': 'mapinfo',
            'File Geodatabase': 'gdb',
            'Geo Package': 'gpkg',
            'MBTILES': 'mbtiles',
            'GeoJson': 'geojson',
            'KML': 'kml',
            'Comma Separated File': 'csv',
            'AutoCAD': 'dxf',
            'MicroStation': 'dgn'
        }
        
        for text, key in output_formats.items():
            self.output_combobox.addItem(text, key)
        
        # Add input browse button
        self.input_browse_button = QtWidgets.QPushButton('Browse', self)
        self.input_browse_button.setGeometry(330, 50, 100, 30)
        self.input_browse_button.clicked.connect(self.browse_input_file)
        
        # Add output browse button
        self.output_browse_button = QtWidgets.QPushButton('Browse', self)
        self.output_browse_button.setGeometry(330, 90, 100, 30)
        self.output_browse_button.clicked.connect(self.browse_output_folder)
        
        # Add fields for name, description, min zoom, max zoom
        self.name_label = QtWidgets.QLabel('Name:', self)
        self.name_label.setGeometry(10, 170, 100, 30)
        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.setGeometry(120, 170, 200, 30)
        
        self.description_label = QtWidgets.QLabel('Description:', self)
        self.description_label.setGeometry(10, 210, 100, 30)
        self.description_edit = QtWidgets.QLineEdit(self)
        self.description_edit.setGeometry(120, 210, 200, 30)
        
        self.min_zoom_label = QtWidgets.QLabel('Min Zoom:', self)
        self.min_zoom_label.setGeometry(10, 250, 100, 30)
        self.min_zoom_spinbox = QtWidgets.QSpinBox(self)
        self.min_zoom_spinbox.setGeometry(120, 250, 200, 30)
        self.min_zoom_spinbox.setValue(0)  # Default value
        
        self.max_zoom_label = QtWidgets.QLabel('Max Zoom:', self)
        self.max_zoom_label.setGeometry(10, 290, 100, 30)
        self.max_zoom_spinbox = QtWidgets.QSpinBox(self)
        self.max_zoom_spinbox.setGeometry(120, 290, 200, 30)
        self.max_zoom_spinbox.setValue(19)  # Default value
        
        # Add convert button
        self.convert_button = QtWidgets.QPushButton('Convert', self)
        self.convert_button.setGeometry(120, 330, 200, 30)
        self.convert_button.clicked.connect(self.convert_vector)

    def browse_input_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "Vector Files (*.zip *.gpkg *.mbtiles *.geojson *.kml *.csv *.dxf *.dgn)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input File", "", file_filter, options=options)
        if file_path:
            self.input_file_path = file_path
            print(f"Selected input file: {file_path}")
    
    def browse_output_folder(self):
        options = QtWidgets.QFileDialog.Options()
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", options=options)
        if folder_path:
            self.output_folder_path = folder_path
            print(f"Selected output folder: {folder_path}")
    
    def convert_vector(self):
        # Get the key associated with the current text in the combobox
        input_key = self.input_combobox.currentData()
        output_format = self.output_combobox.currentData()
        
        # Get the input file path and output folder path
        input_file_path = getattr(self, 'input_file_path', None)
        output_folder_path = getattr(self, 'output_folder_path', None)
        
        if not input_file_path or not output_folder_path:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select both input file and output folder.")
            return

        if input_key == output_format:
            QtWidgets.QMessageBox.warning(self, "Error", "Input and output formats can not be the same!")
            return
        
        # Call your conversion function here
        # Example: convert(input_key, output_format, input_file_path, output_folder_path)
        print(f"Converting from {input_key} to {output_format}")
        print(f"Input file: {input_file_path}")
        print(f"Output folder: {output_folder_path}")
        

        
        
        name = self.name_edit.text()
        description = self.description_edit.text()
        min_zoom = self.min_zoom_spinbox.value()
        max_zoom = self.max_zoom_spinbox.value()

        url = 'http://geodataconverter.online/api/vector/convert'  # Replace with your API endpoint

        output_json = self.post_vector_conversion(input_file_path, output_format, name, description, min_zoom, max_zoom, url)
        self.download_file(output_json["URL"] , output_folder_path)

    def download_file(self,url, dest_folder):
        print("url")
        print(url)
        print("dest_folder")
        print(dest_folder)
        output_path = os.path.join(dest_folder , "output_file.zip")

        # Create a session for persistent cookies and headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Host': 'techmavengeo.cloud',
            # Add any other headers as seen in Postman
        })

        try:
            with session.get(url, stream=True) as response:
                response.raise_for_status()  # Raise error for bad status codes
                with open(output_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            file.write(chunk)
            print(f"Download successful. File saved to: {output_path}")
        except requests.exceptions.RequestException as e:
            print(f"Download failed: {e}")

    def post_vector_conversion(self,input_file_path, output_format, name, description, min_zoom, max_zoom, url):
        # Open the file in binary mode
        with open(input_file_path, 'rb') as file:
            # Prepare the payload for the POST request
            payload = {
                'OutputFormat': output_format,
                'Name': name,
                'Description': description,
                'MinZoom': min_zoom,
                'MaxZoom': max_zoom
            }
            
            # Prepare the files dictionary
            files = {
                'File': file
            }
            
            # Send the POST request
            response = requests.post(url, data=payload, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                # Parse and return the JSON response
                return response.json()
            else:
                # Handle errors
                print(f"Request failed with status code {response.status_code}")
                return response.text