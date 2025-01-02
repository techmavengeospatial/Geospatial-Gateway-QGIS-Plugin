from PyQt5.QtCore import QUrl, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QProgressDialog, QMessageBox

class UploadFile:
    def __init__(self, file_path, company):
        self.file_path = file_path
        self.company = company
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.upload_finished)
        self.progress_dialog = QProgressDialog("Uploading file...", "Cancel", 0, 100)
        self.progress_dialog.setModal(True)
        self.progress_dialog.canceled.connect(self.upload_canceled)

    def upload(self):
        url = QUrl('https://gismapserver.com/upload')  # Replace with actual URL
        request = QNetworkRequest(url)
        file = QFile(self.file_path)
        file.open(QIODevice.ReadOnly)
        reply = self.manager.post(request, file.readAll())
        reply.uploadProgress.connect(self.upload_progress)  # Connect uploadProgress signal
        self.progress_dialog.show()

    def upload_finished(self, reply):
        if reply.error():
            QMessageBox.critical(self, 'Error', f'Failed to upload file: {reply.errorString()}')
        else:
            QMessageBox.information(self, 'Success', 'File uploaded successfully.')
        self.progress_dialog.hide()

    def upload_canceled(self):
        self.manager.abort()
        QMessageBox.warning(self, 'Upload Canceled', 'File upload canceled.')

    def upload_progress(self, bytes_sent, bytes_total):
        progress = int((bytes_sent / bytes_total) * 100)
        self.progress_dialog.setValue(progress)