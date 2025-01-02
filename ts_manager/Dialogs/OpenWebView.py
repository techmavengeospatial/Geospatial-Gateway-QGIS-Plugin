from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QToolBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl

from PyQt5.QtGui import QIcon


class OpenWebView(QDialog):
    def __init__(self, title, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 800)

        # Create a layout
        layout = QVBoxLayout(self)

        # Create a toolbar with a full-screen button
        toolbar = QToolBar()
        full_screen_action = QAction("Full Screen", self)
        full_screen_action.triggered.connect(self.toggle_full_screen)
        toolbar.addAction(full_screen_action)
        layout.addWidget(toolbar)
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        # Create the QWebEngineView
        self.web_view = QWebEngineView()
        print("----------------------------")
        print(url)
        print("----------------------------")
        self.web_view.setUrl(QUrl(url))
        layout.addWidget(self.web_view)

        # Track full-screen state
        self.is_full_screen = False

    def toggle_full_screen(self):
        if self.is_full_screen:
            self.showNormal()
            self.is_full_screen = False
        else:
            self.showFullScreen()
            self.is_full_screen = True