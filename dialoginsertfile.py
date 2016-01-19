# LICENSE: LGPL v3.0

# insert file dialog

from functions import *
from itreefile import IResNode
from widgetsOther import *


class ListViewFile(NoRectangleListWidget):

	pathChanged = Signal(str)

	def __init__(self, root, path, parent=None):
		super().__init__(parent)

		self.root = root
		self.path = ''
		self.isModified = False
		self.currentNode = self.getCurrentNode(path)
		self.pasteBin = None


		self.appearance()
		self.connections()
		self.shortcuts()

		self.updateView()

	def appearance(self):
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		# self.setSelectionMode(QListView.ExtendedSelection)

	def connections(self):
		self.customContextMenuRequested.connect(self.clickedMenu)
		self.itemDoubleClicked.connect(self.actionEnter)

	def shortcuts(self):
		QShortcut(QKeySequence.Copy, self, self.actionCopy)
		QShortcut(QKeySequence.Cut, self, self.actionCut)
		QShortcut(QKeySequence.Paste, self, self.actionPaste)
		QShortcut('F2', self, self.actionRename)
		QShortcut(QKeySequence.Delete, self, self.actionDelete)
		QShortcut(QKeySequence.New, self, self.actionNewFolder)
		QShortcut(QKeySequence.Open, self, self.actionUpload)
		QShortcut(QKeySequence.Save, self, self.actionDownload)
		QShortcut('Right', self, self.actionEnter)
		QShortcut('Left', self, self.actionBack)
		QShortcut(QKeySequence(Qt.Key_Backspace), self, self.actionBack)

	def getCurrentNode(self, path):
		path = path.split('/')
		if path and path[0] == '':
			path = path[1:]
		if path and path[-1] == '':
			path = path[:-1]
		now = self.root
		self.path = '/'
		for name in path:
			pos = now.findName(name)
			if pos == -1:
				self.path = '/'
				return self.root
			self.path += name + '/'
			now = now.at(pos)
		return now

	def makeItem(self, name, isFile):
		item = QListWidgetItem()
		Provider = QFileIconProvider()

		item.setText(name)
		item.setIcon(Provider.icon(QFileIconProvider.File if isFile else QFileIconProvider.Folder))

		return item

	def updateView(self):
		Info = self.currentNode.childrenInfo()
		self.clear()
		for info in Info:
			self.addItem(self.makeItem(info.name, info.isFile))
		# self.setCurrentRow(0)
		self.setCurrentIndex(QModelIndex())

	def makeAction(self, text, slot=None, shortcut=None, isEnable=True, icon=None):
		if not icon:
			icon = QIcon(':/')
		x = QAction(icon, text, self)
		if slot:
			x.triggered.connect(slot)
		if shortcut:
			x.setShortcut(QKeySequence(shortcut))
		x.setEnabled(isEnable)
		return x

	def menuFile(self):
		menu = QMenu(self)
		menu.addAction(self.makeAction(self.tr('Copy'), self.actionCopy, QKeySequence.Copy))
		menu.addAction(self.makeAction(self.tr('Cut'), self.actionCut, QKeySequence.Cut))
		menu.addAction(self.makeAction(self.tr('Paste'), self.actionPaste, QKeySequence.Paste, self.pasteBin != None))
		menu.addAction(self.makeAction(self.tr('Rename'), self.actionRename, 'F2'))
		menu.addAction(self.makeAction(self.tr('Delete'), self.actionDelete, QKeySequence.Delete))
		menu.addSeparator()
		menu.addAction(self.makeAction(self.tr('New Folder'), self.actionNewFolder, QKeySequence.New))
		menu.addAction(self.makeAction(self.tr('Upload'), self.actionUpload, QKeySequence.Open))
		menu.addAction(self.makeAction(self.tr('Download'), self.actionDownload, QKeySequence.Save))
		return menu

	def clickedMenu(self, position):
		""" clicked menu """
		indexes = self.selectedIndexes()
		if indexes:
			menu = self.menuFile()
			menu.exec_(QCursor.pos())

	def getSelectedPath(self):
		index = self.currentItem()
		if index and index.text():
			return self.path + self.currentNode.at(self.currentNode.findName(index.text())).name
		return None

	def getSelectedNode(self):
		index = self.currentItem()
		if index and index.text():
			return self.currentNode.at(self.currentNode.findName(index.text()))
		return None

	def getSelectedNodePointer(self):
		index = self.currentItem()
		if index and index.text():
			return self.currentNode.atPointer(self.currentNode.findName(index.text()))
		return None

	def findInfo(self, parent, name):
		row = 0
		for info in parent.childrenInfo():
			if info.name == name:
				return row, info
			row += 1
		return -1, None

	def actionNewFolder(self):
		name, ok = QInputDialog.getText(None, self.tr("New Folder"), self.tr('Input a string'), QLineEdit.Normal, self.tr('Untitled'))
		if ok:
			if not IResNode.isNameVaild(name):
				QMessageBox.warning(self, self.tr('Error'), self.tr('name is invalid'))
				return
			while self.currentNode.findName(name) != -1:
				name = '-' + name
			self.currentNode.insert(name)
			row, info = self.findInfo(self.currentNode, name)
			self.insertItem(row, self.makeItem(info.name, info.isFile))
			self.setCurrentRow(row)
			self.isModified = True

	def actionCopy(self):
		if self.currentItem():
			self.pasteBin = (self.currentNode, self.currentNode.findName(self.currentItem().text()), 1)

	def actionCut(self):
		if self.currentItem():
			self.pasteBin = (self.currentNode, self.currentNode.findName(self.currentItem().text()), 2)

	def actionPaste(self):
		if self.pasteBin and self.pasteBin[1] != -1:
			parent, row, _ = self.pasteBin
			node = parent.at(row)
			if self.currentNode.isLoop(parent.atPointer(row)):
				QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot copy to itself'))
				return
			pos = self.currentNode.findName(node.name)
			if self.pasteBin[2] == 1:
				if pos != -1 and QMessageBox.warning(self, 'ITree', self.tr('Replace {}?'.format(node.name)), QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Cancel:
					return
				copy = node.copy()
				if pos != -1:
					self.currentNode.remove(pos)
				self.currentNode.insert(copy)

				row, info = self.findInfo(self.currentNode, node.name)
				if pos == -1:
					self.insertItem(row, self.makeItem(info.name, info.isFile))
				self.setCurrentRow(row)
			else:
				if pos != -1 and QMessageBox.warning(self, 'ITree', self.tr('Replace {}?'.format(node.name)), QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Cancel:
					return
				flag = False
				if pos != -1:
					flag = not (parent == self.currentNode and row == pos)
				node = parent.pop(row)
				if flag:
					self.currentNode.remove(pos)
				self.currentNode.insert(node)

				row, info = self.findInfo(self.currentNode, node.name)
				if pos == -1:
					self.insertItem(row, self.makeItem(info.name, info.isFile))
				self.setCurrentRow(row)
			self.isModified = True

	def actionRename(self):
		node = self.getSelectedNode()
		name, ok = QInputDialog.getText(None, self.tr("Rename"), self.tr('Input a string'), QLineEdit.Normal, node.name)
		if ok and node.name != name:
			if not IResNode.isNameVaild(name):
				QMessageBox.warning(self, self.tr('Error'), self.tr('name is invalid'))
				return
			if self.currentNode.findName(name) != -1:
				QMessageBox.warning(self, self.tr('Error'), name + self.tr(' has been existed!'))
				return
			node.name = name
			self.takeItem(self.currentRow())
			row, info = self.findInfo(self.currentNode, name)
			self.insertItem(row, self.makeItem(info.name, info.isFile))
			self.setCurrentRow(row)
			self.pasteBin = None
			self.isModified = True

	def actionDelete(self):
		node = self.getSelectedNode()
		if node:
			if QMessageBox.warning(self, 'ITree', self.tr('Delete it?'), QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Ok:
				row, info = self.findInfo(self.currentNode, node.name)
				self.currentNode.remove(self.currentNode.findName(node.name))
				self.takeItem(row)
				self.pasteBin = None
				self.isModified = True

	def actionUpload(self):
		filename, _ = QFileDialog.getOpenFileName(None, self.tr('Upload'))
		if filename:
			name = os.path.basename(filename)
			while self.currentNode.findName(name) != -1:
				name = '-' + name
			if not self.currentNode.insert(name, filename):
				QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot open file {}'.format(filename)))
			else:
				row, info = self.findInfo(self.currentNode, name)
				self.insertItem(row, self.makeItem(info.name, info.isFile))
				self.setCurrentRow(row)
			self.isModified = True

	def actionDownload(self):
		node = self.getSelectedNode()
		if node and node.isFile():
			filename, _ = QFileDialog.getSaveFileName(None, self.tr('Download'), node.name)
			if filename:
				if not node.data().write(filename):
					QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot save file {}'.format(filename)))

	def actionEnter(self):
		node = self.getSelectedNode()
		if node and not node.isFile():
			self.currentNode = node
			self.updateView()
			self.path += node.name + '/'
			self.pathChanged.emit(self.path)

	def actionBack(self):
		if not self.currentNode.isRoot():
			name = self.currentNode.name
			self.currentNode = self.currentNode.parent()
			self.updateView()
			self.setCurrentRow(self.findInfo(self.currentNode, name)[0])
			self.path = '/'.join(self.path.split('/')[:-2]) + '/'
			self.pathChanged.emit(self.path)


class DialogInsertFile(QDialog):

	def __init__(self, root, path='', parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()

		self.listView = ListViewFile(root, path, self)
		self.path = QLabel(self.listView.path)
		self.path.setMargin(5)
		self.path.setEnabled(False)

		layout = QVBoxLayout()
		layout.addWidget(self.path)
		layout.addWidget(self.listView)
		layout.setContentsMargins(0, 0, 0, 0)

		self.loadSettings()
		self.connections()
		self.setLayout(layout)
		self.setMinimumSize(400, 300)
		self.setWindowTitle(self.tr('File manager'))

	def connections(self):
		self.listView.pathChanged.connect(self.path.setText)

	def loadSettings(self):
		self.mySettings.beginGroup('DialogInsertFile')

		self.restoreGeometry(self.mySettings.value('Geometry'))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogInsertFile')

		self.mySettings.setValue('Geometry', self.saveGeometry())

		self.mySettings.endGroup()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
			if self.listView.getSelectedNode().isFile():
				self.accept()
			else:
				self.listView.actionEnter()
				return
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

	from itreefile import IResNode

	root = IResNode()
	root.insert('hh/a.jpg', 'temp/1.png')
	root.insert('a.jpg', 'temp/1.png')

	p = root.at(root.findName('a.jpg')).dataPointer()
	root.insert('b.jpg', p)

	mainWindow = DialogInsertFile(root, '/')
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
