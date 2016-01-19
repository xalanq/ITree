# LICENSE: LGPL v3.0

# insert picture dialog

from functions import *
from widgetsOther import *
from itreefile import IResNode, IRes


class FileDownloader():

	def __init__(self, url, timeout=20, slotProgress=None):
		self.url = QUrl.fromUserInput(url)
		self.timeout = int(timeout)
		self.slotProgress = slotProgress
		self._data = None

	def start(self):
		loop = QEventLoop()
		manager = QNetworkAccessManager()
		reply = manager.get(QNetworkRequest(self.url))

		tick = QTimer()
		tick.setSingleShot(True)
		tick.start(int(self.timeout * 1000))
		tick.timeout.connect(loop.quit)
		reply.finished.connect(loop.quit)
		if self.slotProgress:
			reply.downloadProgress.connect(self.slotProgress)

		loop.exec_()
		if not tick.isActive():
			return False

		self._data = reply.readAll().data()
		return True

	def data(self):
		return self._data


class ListViewPicture(NoRectangleListWidget):

	def __init__(self, root, parent=None, defaultSize=90):
		super().__init__(parent, 0)

		self.root = root
		self.iconSize = int(defaultSize)
		self.folders = []
		self.currentFolderRow = -1

		self.connections()
		self.shortcuts()
		self.appearance()
		self.getFolders()
		self.updateView()

	def appearance(self):
		self.setViewMode(QListView.IconMode)
		self.setMovement(QListView.Static)
		self.setIconSize(QSize(self.iconSize, self.iconSize))
		self.setUniformItemSizes(True)
		self.setResizeMode(QListWidget.Adjust)

	def connections(self):
		pass

	def shortcuts(self):
		QShortcut(QKeySequence(Qt.Key_Backspace), self, self.actionBack)

	def sizeHint(self):
		return super(QListWidget, self).sizeHint()

	def getFolders(self):
		suffix = [x.data().decode() for x in QImageReader.supportedImageFormats()]

		def _getFolders(root, folder):
			children = root.childrenInfo(False)
			myList = []
			pos = 0
			for info in children:
				child = root.at(pos)
				if info.isFile:
					if [x for x in suffix if info.name.endswith('.' + x)]:
						myList.append(child)
				else:
					_getFolders(child, child.name)
				pos += 1
			if myList:
				myList.sort(key=lambda x: x.name)
				self.folders.append((folder, myList))

		_getFolders(self.root, '/')
		self.folders.sort(key=lambda x: x[0])

	def makeItem(self, name, data):
		pic = QPixmap()
		pic.loadFromData(data)
		icon = QIcon()
		pic = pic.scaled(self.iconSize, self.iconSize)
		icon.addPixmap(pic, QIcon.Normal)
		icon.addPixmap(pic, QIcon.Selected)

		item = QListWidgetItem(icon, name)

		return item

	def updateView(self):
		self.clear()
		if self.currentFolderRow != -1:
			children = self.folders[self.currentFolderRow][1]
			back = QListWidgetItem(QIcon.fromTheme('go-previous'), self.tr('Back'))
			self.addItem(back)
			for child in children:
				self.addItem(self.makeItem(child.name, child.data().toBytes()))
			self.setCurrentIndex(QModelIndex())
		else:
			for item in self.folders:
				name = item[0]
				child = item[1][0]
				self.addItem(self.makeItem(name, child.data().toBytes()))
			self.setCurrentIndex(QModelIndex())

	def actionEnter(self):
		if self.currentFolderRow == -1 and self.currentItem():
			self.currentFolderRow = self.currentRow()
			self.updateView()

	def actionBack(self):
		if self.currentFolderRow != -1:
			self.currentFolderRow = -1
			self.updateView()


class DialogPictureManager(QDialog):

	def __init__(self, root, parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()
		self.listView = ListViewPicture(root, self)

		layout = QVBoxLayout()
		layout.addWidget(self.listView)
		layout.setContentsMargins(0, 0, 0, 0)

		self.loadSettings()
		self.connections()
		self.setLayout(layout)
		self.setMinimumSize(400, 300)
		self.setWindowTitle(self.tr('Picture Manager'))

	def connections(self):
		self.listView.itemClicked.connect(self.slotItemClicked)
		self.listView.itemDoubleClicked.connect(self.slotItemDoubleClicked)

	def loadSettings(self):
		self.mySettings.beginGroup('DialogPictureManager')

		self.restoreGeometry(self.mySettings.value('Geometry'))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogPictureManager')

		self.mySettings.setValue('Geometry', self.saveGeometry())

		self.mySettings.endGroup()

	def currentFile(self):
		node = self.listView.folders[self.listView.currentFolderRow][1][self.listView.currentRow() - 1]
		return node.currentPath() + node.name

	def slotItemClicked(self, item):
		if item:
			if self.listView.currentFolderRow == -1:
				self.listView.setCurrentItem(item)
				self.listView.actionEnter()
			elif self.listView.currentRow() == 0:
				self.listView.setCurrentItem(item)
				self.listView.actionBack()

	def slotItemDoubleClicked(self, item):
		if item:
			if self.listView.currentFolderRow != -1:
				row = self.listView.currentRow()
				if row != 0:
					self.listView.setCurrentItem(item)
					self.accept()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
			if self.listView.currentFolderRow != -1:
				if self.listView.currentRow() == 0:
					self.listView.actionBack()
				else:
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


class DialogInsertPicture(QDialog):

	def __init__(self, root, parent=None):
		super().__init__(parent)
		self.appearance()

		self.mySettings = QSettings()
		self.root = root
		self.picture = QPixmap()
		self.pictureData = b''
		self.previewLastLink = ''
		self.lockK = 0

		self.connections()
		self.loadSettings()
		self.setWindowTitle(self.tr('Insert Picture'))
		self.adjustSize()

	def appearance(self):
		self.lineEditLink = QLineEdit(self)
		self.toolButton = QToolButton(self)
		self.lineEditText = QLineEdit(self)
		self.lineEditTitle = QLineEdit(self)
		self.lineEditWidth = QLineEdit(self)
		self.labelLock = LabelButton(self)
		self.lineEditHeight = QLineEdit(self)
		self.pushButtonSave = QPushButton(self.tr('&Save'), self)
		self.labelDownloadProgress = QLabel(self)
		self.checkBoxPreview = QCheckBox(self.tr('&Preview'), self)
		self.widgetPreview = QLabel(self)

		self.lineEditLink.setPlaceholderText(self.tr('Link'))
		self.lineEditText.setPlaceholderText(self.tr('Text'))
		self.lineEditTitle.setPlaceholderText(self.tr('Title'))
		self.lineEditWidth.setValidator(QIntValidator(1, 99999))
		self.lineEditHeight.setValidator(QIntValidator(1, 99999))
		self.lineEditWidth.setMaximumWidth(70)
		self.lineEditHeight.setMaximumWidth(70)
		self.labelLock.setText('x')
		self.toolButton.setText('...')
		self.labelDownloadProgress.hide()
		self.pushButtonSave.hide()
		self.widgetPreview.hide()
		self.widgetPreview.setFrameStyle(QFrame.NoFrame)
		self.widgetPreview.setAlignment(Qt.AlignCenter)
		self.widgetPreview.setContentsMargins(0, 0, 0, 0)
		self.widgetPreview.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

		layoutUp = QHBoxLayout()
		layoutUp.addWidget(self.lineEditLink)
		layoutUp.addWidget(self.toolButton)
		layoutUp.setSpacing(0)

		layoutDown = QHBoxLayout()
		layoutDown.addWidget(self.lineEditWidth)
		layoutDown.addWidget(self.labelLock)
		layoutDown.addWidget(self.lineEditHeight)
		layoutDown.addStretch()
		layoutDown.addWidget(self.pushButtonSave)
		layoutDown.addWidget(self.labelDownloadProgress)
		layoutDown.addWidget(self.checkBoxPreview)

		layout = QVBoxLayout()
		layout.addLayout(layoutUp)
		layout.addWidget(self.lineEditText)
		layout.addWidget(self.lineEditTitle)
		layout.addLayout(layoutDown)
		layout.addWidget(self.widgetPreview)

		self.setLayout(layout)
		self.setMinimumSize(500, 200)

	def connections(self):
		self.labelLock.clicked.connect(self.lockClicked)
		self.checkBoxPreview.stateChanged.connect(self.actionPreview)
		self.lineEditLink.editingFinished.connect(self.updatePreView)
		self.lineEditWidth.editingFinished.connect(self.updatePreView)
		self.lineEditHeight.editingFinished.connect(self.updatePreView)
		self.lineEditWidth.textChanged.connect(self.lockHeight)
		self.lineEditHeight.textChanged.connect(self.lockWidth)
		self.toolButton.clicked.connect(self.actionSelect)
		self.pushButtonSave.clicked.connect(self.actionSave)

	def loadSettings(self):
		self.mySettings.beginGroup('DialogInsertPicture')

		self.restoreGeometry(self.mySettings.value('Geometry'))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogInsertPicture')

		self.mySettings.setValue('Geometry', self.saveGeometry())

		self.mySettings.endGroup()

	def lockClicked(self):
		self.labelLock.setText('x' if self.labelLock.text() == 'X' else 'X')
		if self.labelLock.text() == 'X' and self.lineEditWidth.text() and self.lineEditHeight.text():
			self.lockK = int(self.lineEditWidth.text()) / int(self.lineEditHeight.text())

	def lockWidth(self, new):
		if self.labelLock.text() == 'X' and new and self.lineEditWidth.text():
			new = int(int(new) * self.lockK)
			if new == 0:
				new = 1
			self.lineEditWidth.textChanged.disconnect(self.lockHeight)
			self.lineEditWidth.setText(str(new))
			self.lineEditWidth.textChanged.connect(self.lockHeight)

	def lockHeight(self, new):
		if self.labelLock.text() == 'X' and new and self.lineEditHeight.text():
			new = int(int(new) / self.lockK)
			if new == 0:
				new = 1
			self.lineEditHeight.textChanged.disconnect(self.lockWidth)
			self.lineEditHeight.setText(str(new))
			self.lineEditHeight.textChanged.connect(self.lockWidth)

	def updateDownloadProgress(self, done, total):
		self.labelDownloadProgress.setText('{} / {} K'.format(int(done / 1024), int(total / 1024)))

	def updatePreView(self):
		if self.checkBoxPreview.isChecked():
			link = self.lineEditLink.text()
			update = False
			self.labelDownloadProgress.setText('')

			if link != self.previewLastLink:
				self.picture = QPixmap()
				self.labelDownloadProgress.show()
				data = DialogInsertPicture.dataFromPath(link, self.root, self.updateDownloadProgress)
				self.labelDownloadProgress.hide()
				if data != None:
					if data[1] == 4:
						self.labelDownloadProgress.setText(self.tr('Timeout'))
						self.labelDownloadProgress.show()
					else:
						self.picture.loadFromData(data[0])
						if not self.picture.isNull():
							self.pictureData = data[0]
							size = self.picture.size()
							if self.labelLock.text() == 'X':
								self.lockClicked()
							self.lineEditWidth.setText(str(size.width()))
							self.lineEditHeight.setText(str(size.height()))
							if self.labelLock.text() == 'x':
								self.lockClicked()
							if data[1] in [2, 3]:
								self.pushButtonSave.show()
							else:
								self.pushButtonSave.hide()

			pic = self.picture
			if not pic.isNull() and self.lineEditWidth.text() and self.lineEditHeight.text():
				size = QSize(int(self.lineEditWidth.text()), int(self.lineEditHeight.text()))
				if pic.size() != size:
					pic = pic.scaled(size)

			if pic.isNull():
				self.pushButtonSave.hide()
				if self.labelLock.text() == 'X':
					self.lockClicked()
				self.lineEditWidth.setText('')
				self.lineEditHeight.setText('')
				self.widgetPreview.setText(self.tr('Can not preview!'))
			else:
				self.widgetPreview.setPixmap(pic)

			self.previewLastLink = link

			self.widgetPreview.show()
			self.setFixedHeight(self.sizeHint().height())
			self.adjustSize()

	def actionPreview(self):
		if self.checkBoxPreview.isChecked():
			self.updatePreView()
		else:
			self.pushButtonSave.hide()
			self.widgetPreview.hide()
			self.setFixedHeight(200)
			self.adjustSize()

	def actionSelect(self):
		dialog = DialogPictureManager(self.root)
		if dialog.exec_() == QDialog.Accepted:
			self.lineEditLink.setText('ifile:' + dialog.currentFile())
			self.lineEditText.setFocus()
			self.updatePreView()

	def actionSave(self):
		name = os.path.basename(self.lineEditLink.text())
		pos = self.root.findName(self.tr('Images'))
		if pos == -1:
			self.root.insert(self.tr('Images'))
			pos = self.root.findName(self.tr('Images'))
		node = self.root.at(pos)
		while node.findName(name) != -1:
			name = '-' + name
		node.insert(name, IRes.fromBytes(self.pictureData))
		self.lineEditLink.setText('ifile:' + node.currentPath() + node.name + '/' + name)
		self.lineEditText.setFocus()
		self.updatePreView()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
			if self.toolButton.hasFocus():
				self.toolButton.animateClick()
			else:
				self.accept()
			return
		if event.key() == Qt.Key_Space:
			if self.labelLock.hasFocus():
				self.lockClicked()
				return

		super().keyPressEvent(event)

	def accept(self):
		self.saveSettings()
		super().accept()

	def reject(self):
		self.saveSettings()
		super().reject()

	@staticmethod
	def dataFromPath(path, root=None, slotProgress=None):
		if root != None and path.startswith('ifile:'):
			path = path[6:]
			if not root.hasNode(path):
				return None
			node = root.getNode(path)
			if not node.isFile():
				return None
			return node.data().toBytes(), 1
		elif os.path.isfile(path):
			data = None
			try:
				data = open(path, 'rb').read()
			except Exception:
				return None
			return data, 2
		else:
			try:
				downloader = FileDownloader(path, int(QSettings().value('Network/Timeout', 20)), slotProgress)
				if not downloader.start():
					return None, 4
				return downloader.data(), 3
			except Exception as e:
				print(e)
				return None


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	from itreefile import IResNode

	root = IResNode()
	for i in range(1, 10):
		root.insert(str(i) + '.png', 'temp/{}.png'.format(i % 5 + 1))
	root.insert('1048237438927482937492384328974234324234234.png', 'temp/1.png')
	for i in range(10, 20):
		root.insert(str(i) + '.png', 'temp/{}.png'.format(i % 5 + 1))

	root.insert('hhhh')
	h = root.at(root.findName('hhhh'))
	for i in range(1, 10):
		h.insert(str(10-i) + '.png', 'temp/{}.png'.format(i % 5 + 1))

	mainWindow = DialogInsertPicture(root)
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()