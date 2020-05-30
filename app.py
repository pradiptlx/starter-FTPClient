import os
import sys
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from model.FTPClientModel import FTPClientModel
from view.UiFtpClient import UiFTPClient


class LocalListWidget(QListWidget):
    def __init__(self, parent: QListWidget):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.CopyAction)

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        print(e)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls():
            print(event.mimeData().data('text/uri-list'))


class RemoteListWidget(QListWidget):
    def __init__(self, parent: QListWidget):
        super().__init__(parent)
        self.setAcceptDrops(parent.acceptDrops())
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.CopyAction)

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        print(e)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                print(url.toLocalFile())
        else:
            event.ignore()


# For context menu action
def delete_action(parent):
    action = QAction("Delete", parent)

    return action


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
    remoteHist = []
    remoteListTree = {}

    currentLocalDir = "./"
    currentRemoteDir = "/"

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.contextMenuRemote = QMenu()
        self.iconFile = QtGui.QIcon(os.path.abspath('view/icon/document-list.png'))
        self.iconDir = QtGui.QIcon(os.path.abspath('view/icon/folder.png'))
        self.client = FTPClientModel()
        self.setupUi(self)
        self.remoteListWidget = RemoteListWidget(self.horizontalLayoutWidget)
        self.localListWidget = LocalListWidget(self.horizontalLayoutWidget)
        self.containerLocalDir.addWidget(self.localListWidget)
        self.containerRemoteDir.addWidget(self.remoteListWidget)

        self.connectBtn.pressed.connect(self.connect_slot)
        self.filesystem_model()

        self.localTreeDir.expanded.connect(self.clicked_tree_view_local)
        self.localTreeDir.expandsOnDoubleClick()
        self.localListWidget.itemChanged.connect(self.list_item_changed)

        self.remoteTreeDir.itemDoubleClicked.connect(self.parsing_folder_remote)
        self.remoteTreeDir.itemCollapsed.connect(self.remove_collapsed_tree_remote)
        # self.remoteListWidget.customContextMenuRequested.connect(self.delete_context_menu_remote)
        # self.register_context_menu_remote()
        self.remoteListWidget.itemChanged.connect(self.remote_list_widget_item_changed)

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

            self.parsing_remote_tree_widget(self.remoteDir)
        else:
            self.client.disconnect()
            self.connectBtn.setText('Connect')
            self.remoteTreeDir.clear()
            self.remoteListWidget.clear()

    def filesystem_model(self, path="."):
        self.fsModel = QFileSystemModel()
        self.fsModel.setRootPath(path)

        self.render_tree_view(self.fsModel, QDir(path), self.localTreeDir)
        self.parsing_list_widget(path, self.localListWidget)

    def clicked_tree_view_local(self, index: QModelIndex):
        self.fsModel.flags(index)
        path = self.fsModel.fileInfo(index).absoluteFilePath()
        self.currentLocalDir = path
        self.parsing_list_widget(path, self.localListWidget)
        # self.render_tree_view(self.fsModel, path, self.localTreeDir)

    def parsing_list_widget(self, path, view: QListWidget):
        view.clear()
        for file in os.listdir(path):
            fullpath = os.path.join(self.currentLocalDir, file)
            if Path(fullpath).is_file():
                itemWidget = QListWidgetItem()
                itemWidget.setIcon(self.iconFile)
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
        self.remoteHist.append(path)
        self.currentRemoteDir = os.path.join(self.client.curr_dir(), path)
        self.remoteDir = self.client.change_dir(path)

    def parsing_remote_tree_widget(self, dirs):
        global icon
        list_files = []
        for file in dirs:
            type_file = file[1]['type']
            if type_file == 'file':
                icon = self.iconFile
                list_files.append(file)
            elif type_file == 'dir':
                icon = self.iconDir
            treeWidget = QTreeWidgetItem()
            treeWidget.setIcon(0, icon)
            treeWidget.setText(0, file[0])
            treeWidget.setText(1, type_file)
            treeWidget.setText(2, self.currentRemoteDir + '/' + file[0])
            self.remoteTreeDir.addTopLevelItem(treeWidget)
        self.parsing_remote_list_widget(list_files)

    def parsing_remote_child_tree_widget(self, parent: QTreeWidgetItem, dirs):
        global icon
        list_files = []
        list_folders = []
        for file in dirs:
            type_file = file[1]['type']
            if type_file == 'file':
                list_files.append(file)
                icon = self.iconFile
            elif type_file == 'dir':
                list_folders.append(file[0])
                icon = self.iconDir
            treeWidget = QTreeWidgetItem()
            treeWidget.setIcon(0, icon)
            treeWidget.setText(0, file[0])
            treeWidget.setText(1, type_file)
            treeWidget.setText(2, self.currentRemoteDir + '/' + file[0])
            parent.addChild(treeWidget)
        self.remoteListTree[self.remoteHist[-1]] = list_folders
        self.parsing_remote_list_widget(list_files)

    # TODO: Context menu
    # def register_context_menu_remote(self):
    #     self.contextMenuRemote.addAction(delete_action(self.remoteListWidget))

    def parsing_remote_list_widget(self, list_files):
        self.remoteListWidget.clear()
        for file in list_files:
            itemListWidget = QListWidgetItem()
            itemListWidget.setIcon(self.iconFile)
            itemListWidget.setText(file[0])
            self.remoteListWidget.addItem(itemListWidget)

    def remote_list_widget_item_changed(self, item: QListWidgetItem):
        # UPLOAD TO REMOTE
        print(item.text())

    # Slot for itemClicked
    def parsing_folder_remote(self, item: QTreeWidgetItem, column: QColumnView):
        if item.text(1) == 'dir':
            # self.change_dir_remote(os.path.join(self.currentRemoteDir, item.text(0)))
            self.change_dir_remote(item.text(2))
            print(self.remoteHist)
            print(self.currentRemoteDir)

            self.parsing_remote_child_tree_widget(item, self.remoteDir)
            print(self.remoteListTree)

    @staticmethod
    def remove_collapsed_tree_remote(item: QTreeWidgetItem):
        item.takeChildren()

    # def parsing_path_remote(self, path):
    #     for parent in self.remoteListTree.keys():
    #         newPath = path
    #         isChild = False
    #         if path in parent.items():
    #             isChild = True
    #             newPath = parent + "/" + path

    def context_menu_remote_delete(self, position):
        pass

    def create_remote_menu(self):
        pass


# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec_()
