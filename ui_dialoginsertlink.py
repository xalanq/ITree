# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialoginsertlink.ui'
#
# Created: Sat Jan 16 00:31:33 2016
#      by: pyside-uic 0.2.13 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_DialogInsertLink(object):
    def setupUi(self, DialogInsertLink):
        DialogInsertLink.setObjectName("DialogInsertLink")
        DialogInsertLink.resize(400, 152)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogInsertLink.sizePolicy().hasHeightForWidth())
        DialogInsertLink.setSizePolicy(sizePolicy)
        DialogInsertLink.setMinimumSize(QtCore.QSize(400, 0))
        DialogInsertLink.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtGui.QVBoxLayout(DialogInsertLink)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEditLink = QtGui.QLineEdit(DialogInsertLink)
        self.lineEditLink.setObjectName("lineEditLink")
        self.horizontalLayout.addWidget(self.lineEditLink)
        self.toolButton = QtGui.QToolButton(DialogInsertLink)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lineEditText = QtGui.QLineEdit(DialogInsertLink)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditText.sizePolicy().hasHeightForWidth())
        self.lineEditText.setSizePolicy(sizePolicy)
        self.lineEditText.setObjectName("lineEditText")
        self.verticalLayout.addWidget(self.lineEditText)
        self.lineEditTitle = QtGui.QLineEdit(DialogInsertLink)
        self.lineEditTitle.setObjectName("lineEditTitle")
        self.verticalLayout.addWidget(self.lineEditTitle)

        self.retranslateUi(DialogInsertLink)
        QtCore.QMetaObject.connectSlotsByName(DialogInsertLink)

    def retranslateUi(self, DialogInsertLink):
        DialogInsertLink.setWindowTitle(QtGui.QApplication.translate("DialogInsertLink", "Insert a link", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditLink.setPlaceholderText(QtGui.QApplication.translate("DialogInsertLink", "Link", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("DialogInsertLink", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditText.setPlaceholderText(QtGui.QApplication.translate("DialogInsertLink", "Text", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditTitle.setPlaceholderText(QtGui.QApplication.translate("DialogInsertLink", "Title", None, QtGui.QApplication.UnicodeUTF8))

