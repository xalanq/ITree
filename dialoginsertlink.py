# LICENSE: LGPL v3.0

# insert link dialog

from functions import *
from ui_dialoginsertlink import Ui_DialogInsertLink


class DialogFileFolder(QFileDialog):
	""" choose file/folder  """

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setFileMode(QFileDialog.Directory)
		self.setOption(QFileDialog.DontUseNativeDialog, True)
		self.listView = self.findChild(QListView, 'listView')
		self.treeView = self.findChild(QTreeView)
		self.setNameFilter(self.tr('Any file/folder (*)'))
		for button in self.findChildren(QPushButton):
			if '&C' in button.text():
				self.button = button
				break
		for label in self.findChildren(QLabel):
			if label.buddy() != None:
				label.setText(self.tr('File/Folder'))
		if self.listView:
			self.listView.setSelectionMode(QAbstractItemView.SingleSelection)
		if self.treeView:
			self.treeView.setSelectionMode(QAbstractItemView.SingleSelection)
		self.button.installEventFilter(self)
		self.button.clicked.disconnect()
		self.button.clicked.connect(self.chooseClicked)
		self.setWindowTitle(self.tr('Select A File/Folder'))

	def mySelectedIndexes(self):
		arr = []
		for index in self.listView.selectionModel().selectedIndexes():
			if index.column() == 0:
				arr.append(self.directory().absolutePath() + '/' + index.data())
		return arr

	def eventFilter(self, item, event):
		if item and type(item) == QPushButton and '&C' in item.text():
			if event.type() == QEvent.EnabledChange:
				if not item.isEnabled():
					item.setEnabled(True)
		return super().eventFilter(item, event)

	def chooseClicked(self):
		self.done(QFileDialog.Accepted)

	def selectedFiles(self):
		return self.mySelectedIndexes()


class DialogInsertLink(QDialog, Ui_DialogInsertLink):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)

		self.mySettings = QSettings()

		self.loadSettings()
		self.connections()
		self.setFixedHeight(self.sizeHint().height())

	def loadSettings(self):
		self.mySettings.beginGroup('DialogInsertLink')

		self.restoreGeometry(self.mySettings.value('Geometry'))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogInsertLink')

		self.mySettings.setValue('Geometry', self.saveGeometry())

		self.mySettings.endGroup()

	def connections(self):
		self.toolButton.clicked.connect(self.open)

	def open(self):
		file = DialogFileFolder()
		if file.exec_() == QFileDialog.Accepted:
			files = file.selectedFiles()
			if files:
				self.lineEditLink.setText(files[0])

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
			if self.toolButton.hasFocus():
				self.toolButton.animateClick()
			else:
				self.accept()
		super().keyPressEvent(event)

	def accept(self):
		self.saveSettings()
		super().accept()

	def reject(self):
		self.saveSettings()
		super().reject()


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	mainWindow = DialogInsertLink()
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()