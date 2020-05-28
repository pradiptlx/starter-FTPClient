from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from view.UiFtpClient import UiFTPClient
from model.FTPClientModel import FTPClientModel
import sys, os
from pathlib import Path


class LocalListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(72, 72))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                print(url)
                links.append(str(url.toLocalFile()))
            self.emit(PYQT_SIGNAL("dropped"), links)
        else:
            event.ignore()


# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow, UiFTPClient):
    client = None
    username = "dex"
    password = "123"
    host = '127.0.0.1'
    port = 8009

    fsModel = None
    remoteModel = None

    remoteDir = []
    currentLocalDir = "."

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.client = FTPClientModel()
        self.setupUi(self)

        self.connectBtn.pressed.connect(self.connect_slot)
        self.filesystem_model()

        self.localTreeDir.expanded.connect(self.clicked_tree_view_local)
        self.localTreeDir.expandsOnDoubleClick()

        self.localListFile.itemChanged.connect(self.list_item_changed)

        self.remoteTreeDir.itemClicked.connect(self.parsing_folder_remote)

    def connect_slot(self):
        if not self.client.isConnected:
            self.username = self.usernameInput.text()
            self.password = self.passwordInput.text()
            self.host = self.hostInput.text()
            self.port = int(self.portInput.text())

            self.client.connect(self.username, self.password,
                                self.host, self.port)
            self.connectBtn.setText('Disconnect')

            self.remoteDir = self.client.list_dir('.')

            self.remote_filesystem_model()
            # self.remoteTreeDir.expand(self.clicked_tree_view_remote)
        else:
            self.client.disconnect()
            self.connectBtn.setText('Connect')
            self.remoteTreeDir.clear()
            self.remoteListFile.clear()

    def filesystem_model(self, path="."):
        self.fsModel = QFileSystemModel()
        self.fsModel.setRootPath(path)

        self.render_tree_view(self.fsModel, QDir(path), self.localTreeDir)

    def clicked_tree_view_local(self, index: QModelIndex):
        self.fsModel.flags(index)
        path = self.fsModel.fileInfo(index).absoluteFilePath()
        self.currentLocalDir = path
        self.parsing_list_widget(path, self.localListFile)
        # self.render_tree_view(self.fsModel, path, self.localTreeDir)

    def parsing_list_widget(self, path, view: QListWidget):
        view.clear()
        print(view.supportedDropActions())
        for file in os.listdir(path):
            fullpath = os.path.join(self.currentLocalDir, file)
            if Path(fullpath).is_file():
                itemWidget = QListWidgetItem()
                itemWidget.setText(file)
                view.addItem(itemWidget)

    def list_item_changed(self, item: QListWidgetItem):
        fname = os.path.join(self.currentLocalDir, item.text())
        dest = os.path.join(self.currentLocalDir, item.text() + '_')
        print(fname)

        with open(dest, 'w') as file:
            fd = open(fname, 'r')
            file.writelines(fd.readlines())
            fd.close()

    @staticmethod
    def render_tree_view(fsModel: QFileSystemModel, path: QDir, view: QTreeView):
        view.setModel(fsModel)
        view.setRootIndex(fsModel.index(path.absolutePath()))
        view.setDragDropMode(QAbstractItemView.InternalMove)

    # REMOTE
    def get_list_dir_remote(self, path="."):
        self.remoteDir = self.client.list_dir(path)

    def change_dir_remote(self, path):
        self.remoteDir = self.client.change_dir(path)

    def remote_filesystem_model(self, path="."):
        self.remoteModel = QFileSystemModel()
        self.remoteModel.setRootPath(path)
        self.get_list_dir_remote(path)
        print(self.remoteDir)

        self.parsing_remote_tree_widget(self.remoteDir)
        # self.render_tree_view(self.remoteModel, QDir(path), self.remoteTreeDir)

    def parsing_remote_tree_widget(self, dirs):
        list_files = []
        for file in dirs:
            type_file = file[1]['type']
            if type_file == 'file':
                list_files.append(file)
            treeWidget = QTreeWidgetItem()
            treeWidget.setText(0, file[0])
            treeWidget.setText(1, type_file)
            self.remoteTreeDir.addTopLevelItem(treeWidget)
        self.parsing_remote_list_widget(list_files)

    def parsing_remote_child_tree_widget(self, parent: QTreeWidgetItem, dirs):
        list_files = []
        for file in dirs:
            type_file = file[1]['type']
            if type_file == 'file':
                list_files.append(file)
            treeWidget = QTreeWidgetItem()
            treeWidget.setText(0, file[0])
            treeWidget.setText(1, type_file)
            parent.addChild(treeWidget)

    def parsing_remote_list_widget(self, list_files):
        for file in list_files:
            itemListWidget = QListWidgetItem()
            itemListWidget.setText(file[0])
            self.remoteListFile.addItem(itemListWidget)

    # Slot for itemClicked
    def parsing_folder_remote(self, item: QTreeWidgetItem, column: QColumnView):
        if item.text(1) == 'dir':
            self.change_dir_remote(item.text(0))

            self.parsing_remote_child_tree_widget(item, self.remoteDir)


def clicked_tree_view_remote(self, index: QModelIndex):
    path = self.remoteModel.fileInfo(index).absoluteFilePath()
    print(path)
    self.render_tree_view(self.remoteModel, path, self.remoteTreeDir)


# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec_()
