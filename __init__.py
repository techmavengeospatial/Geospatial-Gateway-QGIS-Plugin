# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TSManager
                                 A QGIS plugin
 The LTG Api plugin for QGIS is a powerful tool that enables users to seamlessly interact with online Live Tech Geo API. With this plugin, users can upload static GIS files, including MBTiles and other static files, for later use. Additionally, it allows for the conversion of vector files into various formats such as shapefile, geojson, kml, and mbtiles, which can then be published to a new table in PostGIS, making them accessible as XYZ tiles. Furthermore, users can upload custom styles to enhance their data visualization. The plugin also provides a convenient way to browse static GIS files hosted on the server and explore pg_featureserv endpoints, making it a comprehensive solution for working with online LTG API in QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-07-11
        copyright            : (C) 2024 by Tech Maven Geospatial
        email                : jordan@techmaven.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import os
import sys
import subprocess
from qgis.PyQt.QtWidgets import QMessageBox

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TSManager class from file TSManager.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    install_requirements()
    from .TS_Manager import TSManager
    return TSManager(iface)


def install_requirements():
    try:
        # Check for correct batch file on Windows
        qgis_bin_dir = os.path.dirname(sys.executable)

        # Try both python-qgis.bat and python-qgis.ltr.bat
        python_qgis_bat = os.path.join(qgis_bin_dir, "python-qgis.bat")
        python_qgis_ltr_bat = os.path.join(qgis_bin_dir, "python-qgis-ltr.bat")
        print(python_qgis_ltr_bat)
        if os.path.exists(python_qgis_ltr_bat):
            python_qgis = python_qgis_ltr_bat
        elif os.path.exists(python_qgis_bat):
            python_qgis = python_qgis_bat
        else:
            raise FileNotFoundError("No QGIS Python batch file found.")

        # Path to requirements.txt
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

        # Install requirements
        subprocess.check_call([python_qgis, "-m", "pip", "install", "-r", requirements_path])

    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, "Error", f"Failed to install dependencies: {str(e)}")
    except FileNotFoundError as e:
        QMessageBox.critical(None, "Error", f"QGIS Python batch file not found for Geospatial Gateway - GeospatialCloudServ and Tile Server Connection plugin: {str(e)}")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(e)}")