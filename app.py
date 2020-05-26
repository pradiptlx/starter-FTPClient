from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from view.UiFtpClient import UiFTPClient
from model.FTPClientModel import FTPClientModel
import sys


# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow, UiFTPClient):
    client = None
    username = "dex"
    password = "123"
    host = '127.0.0.1'
    port = 8009

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.client = FTPClientModel()
        self.setupUi(self)

        self.connectBtn.pressed.connect(self.connect_slot)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # Slot for input
    def connect_slot(self):
        if not self.client.isConnected:
            self.username = self.usernameInput.text()
            self.password = self.passwordInput.text()
            self.host = self.hostInput.text()
            self.port = int(self.portInput.text())

            self.client.connect(self.username, self.password,
                                self.host, self.port)

            list_dir = self.client.list_dir('.')

            self.create_scroll(list_dir)

        elif self.client.isConnected:
            self.connectBtn.setText('Disconnect')

    def create_scroll(self, list_dir):
        vbox = QVBoxLayout()
        wdgt = QWidget()

        for i in range(len(list_dir['filenames'])):
            qlab = QLabel(str(list_dir['filenames'][i]))
            vbox.addWidget(qlab)
        wdgt.setLayout(vbox)
        self.scrollArea.setWidget(wdgt)


# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec_()
