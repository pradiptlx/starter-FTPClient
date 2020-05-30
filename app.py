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

    # def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
    #     e.accept()
    #     print(e.pos())

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            print(e.mimeData().hasText())

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                print(path)


class RemoteListWidget(QListWidget):
    dropped = pyqtSignal(str)  # Dropped file signal

    def __init__(self, parent: QListWidget):
        super().__init__(parent)
        self.setAcceptDrops(parent.acceptDrops())
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.CopyAction)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            print(event)
            event.ignore()

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            print(e.mimeData().text())

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                # print(url.toLocalFile())
                self.dropped.emit(url.toLocalFile())
                listItem = QListWidgetItem()
                fname = os.path.basename(url.toLocalFile())
                listItem.setText(fname)
                listItem.setIcon(QtGui.QIcon(os.path.abspath('view/icon/document-list.png')))
                self.addItem(listItem)
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
    url = None

    fsModel = None
    remoteModel = None

    remoteDir = []
    remoteHist = []
    remoteListTree = {}

    currentLocalDir = "./"
    currentRemoteDir = "/"

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.iconFile = QtGui.QIcon(os.path.abspath('view/icon/document-list.png'))
        self.iconDir = QtGui.QIcon(os.path.abspath('view/icon/folder.png'))
        self.client = FTPClientModel()
        self.setupUi(self)
        self.actionExit.triggered.connect(qApp.quit)
        self.actionAboutMe.triggered.connect(self.menu_about)
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
        self.remoteListWidget.dropped.connect(self.upload_file_to_remote)
        self.remoteListWidget.installEventFilter(self)

    def eventFilter(self, widget: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.ContextMenu and widget is self.remoteListWidget:
            item = widget.itemAt(event.pos())
            filename = item.text()
            menu = QMenu()
            downloadAction = QAction("Download", self)
            deleteAction = QAction('Delete File Remote', self)
            menu.addAction(downloadAction)
            menu.addSeparator()
            menu.addAction(deleteAction)
            downloadAction.triggered.connect(lambda: self.download_file_from_remote(filename))
            deleteAction.triggered.connect(lambda: self.delete_file_from_remote(filename))

            menu.exec_(event.globalPos())
            return True
        return super(MainWindow, self).eventFilter(widget, event)

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
        self.fsModel.setRootPath(path)
        # print(self.fsModel.data(index, Qt.StatusTipRole))
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
                itemWidget.setData(Qt.UserRole, fullpath)
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

    def parsing_remote_list_widget(self, list_files):
        self.remoteListWidget.clear()
        for file in list_files:
            itemListWidget = QListWidgetItem()
            itemListWidget.setIcon(self.iconFile)
            itemListWidget.setText(file[0])
            self.remoteListWidget.addItem(itemListWidget)

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

    def refresh_remote_list_widget(self):
        self.get_list_dir_remote(self.currentRemoteDir)
        list_files= []
        for file in self.remoteDir:
            type_file = file[1]['type']
            if type_file == 'file':
                list_files.append(file)
        self.parsing_remote_list_widget(list_files)

    def delete_file_from_remote(self, filename):
        self.client.delete_file(filename)
        self.refresh_remote_list_widget()

    def download_file_from_remote(self, filename):
        self.client.download(filename, os.path.join(self.currentLocalDir, filename))

    @pyqtSlot(str)
    def upload_file_to_remote(self, url):
        if self.client.isConnected:
            fname = os.path.basename(url)
            self.client.upload(url, fname)
            self.get_list_dir_remote(self.currentRemoteDir)

    # def parsing_path_remote(self, path):
    #     for parent in self.remoteListTree.keys():
    #         newPath = path
    #         isChild = False
    #         if path in parent.items():
    #             isChild = True
    #             newPath = parent + "/" + path
    @staticmethod
    def menu_about():
        box = QMessageBox()
        box.setWindowTitle("About Me")
        box.setText("Hey there, this app created by Akwila Feliciano, for my Network Programming project.")
        box.exec_()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
