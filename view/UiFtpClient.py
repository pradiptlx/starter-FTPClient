# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FtpClient.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class UiFTPClient(object):
    def setupUi(self, FTPClient):
        FTPClient.setObjectName("FTPClient")
        FTPClient.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FTPClient.sizePolicy().hasHeightForWidth())
        FTPClient.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(FTPClient)
        self.centralwidget.setObjectName("centralwidget")
        self.usernameInput = QtWidgets.QLineEdit(self.centralwidget)
        self.usernameInput.setGeometry(QtCore.QRect(10, 90, 113, 20))
        self.usernameInput.setObjectName("usernameInput")
        self.usernameLabel = QtWidgets.QLabel(self.centralwidget)
        self.usernameLabel.setGeometry(QtCore.QRect(10, 70, 61, 21))
        self.usernameLabel.setObjectName("usernameLabel")
        self.passwordLabel = QtWidgets.QLabel(self.centralwidget)
        self.passwordLabel.setGeometry(QtCore.QRect(10, 140, 47, 13))
        self.passwordLabel.setObjectName("passwordLabel")
        self.passwordInput = QtWidgets.QLineEdit(self.centralwidget)
        self.passwordInput.setGeometry(QtCore.QRect(10, 160, 113, 20))
        self.passwordInput.setObjectName("passwordInput")
        self.portLabel = QtWidgets.QLabel(self.centralwidget)
        self.portLabel.setGeometry(QtCore.QRect(10, 220, 47, 13))
        self.portLabel.setObjectName("portLabel")
        self.portInput = QtWidgets.QLineEdit(self.centralwidget)
        self.portInput.setGeometry(QtCore.QRect(10, 240, 51, 20))
        self.portInput.setObjectName("portInput")
        self.hostInput = QtWidgets.QLineEdit(self.centralwidget)
        self.hostInput.setGeometry(QtCore.QRect(10, 30, 113, 20))
        self.hostInput.setText("")
        self.hostInput.setObjectName("hostInput")
        self.hostLabel = QtWidgets.QLabel(self.centralwidget)
        self.hostLabel.setGeometry(QtCore.QRect(10, 10, 61, 21))
        self.hostLabel.setObjectName("hostLabel")
        self.connectBtn = QtWidgets.QPushButton(self.centralwidget)
        self.connectBtn.setGeometry(QtCore.QRect(10, 290, 75, 23))
        self.connectBtn.setObjectName("connectBtn")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(130, 0, 671, 561))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 669, 559))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        FTPClient.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(FTPClient)
        self.statusbar.setObjectName("statusbar")
        FTPClient.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(FTPClient)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        FTPClient.setMenuBar(self.menubar)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(FTPClient)
        QtCore.QMetaObject.connectSlotsByName(FTPClient)

    def retranslateUi(self, FTPClient):
        _translate = QtCore.QCoreApplication.translate
        FTPClient.setWindowTitle(_translate("FTPClient", "FTPClient"))
        self.usernameLabel.setText(_translate("FTPClient", "Username"))
        self.passwordLabel.setText(_translate("FTPClient", "Password"))
        self.portLabel.setText(_translate("FTPClient", "Port"))
        self.hostLabel.setText(_translate("FTPClient", "Host"))
        self.connectBtn.setText(_translate("FTPClient", "Connect"))
        self.menuMenu.setTitle(_translate("FTPClient", "Menu"))
        self.menuAbout.setTitle(_translate("FTPClient", "About"))
