import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from qgis.PyQt.QtCore import QSettings
import requests
import json
from urllib.parse import urljoin

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)

        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configurations.json')
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}
        pocketbaseUrl = config.get("PocketBase")

        if pocketbaseUrl:
            self.loginUrl = urljoin(pocketbaseUrl, '/api/collections/users/auth-with-password')

            self.verifyLogin = urljoin(pocketbaseUrl, '/api/collections/users/auth-with-password')
        # Logo
            self.logo_label = QtWidgets.QLabel(self)
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) , "icon.png")
            self.logo_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), icon_path))
            self.logo_label.setPixmap(self.logo_pixmap.scaled(200, 50, QtCore.Qt.KeepAspectRatio))
            self.logo_label.setAlignment(QtCore.Qt.AlignCenter)

            # Title
            self.title_label = QtWidgets.QLabel("Tile Server Manager", self)
            font = self.title_label.font()
            font.setPointSize(14)
            font.setBold(True)
            self.title_label.setFont(font)
            self.title_label.setAlignment(QtCore.Qt.AlignCenter)

            # Username field
            self.username_label = QtWidgets.QLabel("Username:", self)
            self.username_input = QtWidgets.QLineEdit(self)
            self.username_input.setText("")
            self.username_input.setPlaceholderText("Enter your username")
            self.username_input.setFixedHeight(30)

            # Password field
            self.password_label = QtWidgets.QLabel("Password:", self)
            self.password_input = QtWidgets.QLineEdit(self)
            self.password_input.setText("")
            self.password_input.setPlaceholderText("Enter your password")
            self.password_input.setFixedHeight(30)
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

            # Login button
            self.login_button = QtWidgets.QPushButton("Login", self)
            self.login_button.setFixedHeight(40)
            self.login_button.clicked.connect(self.login)

            # Layouts
            self.layout = QtWidgets.QVBoxLayout()
            self.layout.addWidget(self.logo_label)
            self.layout.addWidget(self.title_label)
            self.layout.addSpacing(10)
            self.layout.addWidget(self.username_label)
            self.layout.addWidget(self.username_input)
            self.layout.addSpacing(10)
            self.layout.addWidget(self.password_label)
            self.layout.addWidget(self.password_input)
            self.layout.addSpacing(20)
            self.layout.addWidget(self.login_button)

            self.setLayout(self.layout)
        else:
            self.layout = QtWidgets.QVBoxLayout()
            self.layout.addWidget(QtWidgets.QLabel('No Authentication Url Defined'))
            self.layout.addSpacing(10)

            self.config_button = QtWidgets.QPushButton("Configure", self)
            self.config_button.setFixedHeight(40)
            self.config_button.clicked.connect(self.login)
            self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        data = {'identity': username, 'password': password}

        response = requests.post(self.loginUrl, json=data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data['token']
            if token:
                # Store the token securely using QSettings
                settings = QSettings()
                settings.setValue('plugin/token', token)
                QtWidgets.QMessageBox.information(self, "Login Successful", "You have successfully logged in.")
                self.accept()  # Close the dialog
                return True
            else:
                QtWidgets.QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")
                return False
        return False

    def logout(self):
        # Access QSettings
        settings = QSettings()

        # Check if the token exists
        token = settings.value('plugin/token', None)

        if token:
            # Remove the token
            settings.remove('plugin/token')
            QtWidgets.QMessageBox.information(self, "Logout Successful", "You have been logged out.")
        else:
            QtWidgets.QMessageBox.warning(self, "Logout", "You are not logged in.")

    def verify_login(self):
        settings = QSettings()
        token = settings.value('plugin/token', None)
        if token:
            return True
        return False

    def verify_login_online(self):
        # Retrieve the stored token
        settings = QSettings()
        token = settings.value('plugin/token', None)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(self.verifyLogin, headers=headers)

            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                # Unauthorized, token might have expired
                return False
        return False

