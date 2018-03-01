# LICENSE: LGPL v3.0
# see the file "LICENSE"

# mainwindow

from functions import *
from itreefile import INode, IResNode, ITreeFile
from dialogs import *
from widgets import *
from ifont import *


class MainWindow(QMainWindow):
	""" ************************************************* main view ************************************************* """

	def __init__(self, parent=None):
		super().__init__(parent)

		self.nodeRoot = INode()
		self.resRoot = IResNode()
		self.mySettings = QSettings()
		self.mainWidget = MainWidget(self)
		self.isResModified = False
		self.currentFileName = ''
		self.resCurrentPath = '/'

		self.appearance()
		self.actions()
		self.shortcuts()
		self.loadSettings()
		self.connections()
		self.setCurrentName('')
		self.setCentralWidget(self.mainWidget)
		self.setMinimumSize(QSize(800, 600))
		self.setCenter()

	def makeAction(self, text, slot=None, shortcut=None, icon=None):
		if not icon:
			icon = QIcon(':/')
		x = QAction(icon, text, self)
		if slot:
			x.triggered.connect(slot)
		if shortcut:
			x.setShortcut(QKeySequence(shortcut))
			self.addAction(x)
		return x

	def connections(self):
		""" connections """
		self.mainWidget.treeView.customContextMenuRequested.connect(self.clickedMenu)
		self.mainWidget.contentsChanged.connect(self.updateModified)

	def loadSettings(self):
		""" load settings """

		self.mySettings.beginGroup('MainWindow')

		self.restoreGeometry(self.mySettings.value('Geometry'))
		self.restoreState(self.mySettings.value('State'))
		self.menuBar().setVisible(self.mySettings.value('Menu/Visible', 'true') == 'true')

		QApplication.setFont(loadFont(self.mySettings, QFont()))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('MainWindow')
		self.mySettings.setValue('Geometry', self.saveGeometry())
		self.mySettings.setValue('State', self.saveState())
		self.mySettings.setValue('Menu/Visible', self.menuBar().isVisible())
		self.mySettings.endGroup()
		self.mainWidget.saveSettings()

	def settingsChanged(self):
		self.mySettings.beginGroup('MainWindow')
		QApplication.setFont(loadFont(self.mySettings, QFont()))
		self.mySettings.endGroup()
		self.mainWidget.loadSettings()

	def actions(self):
		self.actionRedo.setEnabled(False)
		self.actionUndo.setEnabled(False)

		self.mainWidget.undoStack.canRedoChanged.connect(self.actionRedo.setEnabled)
		self.mainWidget.undoStack.canUndoChanged.connect(self.actionUndo.setEnabled)

	def shortcuts(self):
		""" init shortcut """
		pass

	def appearance(self):
		self.actionOpen = self.makeAction(self.tr('&Open'), self.openFile, QKeySequence.Open)
		self.actionSave = self.makeAction(self.tr('&Save'), self.saveFile, QKeySequence.Save)
		self.actionSaveAs = self.makeAction(self.tr('&Save As'), self.saveAsFile, QKeySequence.SaveAs)
		self.actionClose = self.makeAction(self.tr('&Close'), self.closeFile, QKeySequence.Close)
		self.actionQuit = self.makeAction(self.tr('&Quit'), self.close, QKeySequence.Quit)

		self.actionPreference = self.makeAction(self.tr('&Preference'), self.preference, 'Ctrl+P')
		self.actionInsertCode = self.makeAction(self.tr('Insert &Code'), self.insertCode, 'Ctrl+H')
		self.actionInsertFile = self.makeAction(self.tr('Insert &File'), self.insertFile, 'Ctrl+J')
		self.actionInsertLink = self.makeAction(self.tr('Insert &Link'), self.insertLink, 'Ctrl+K')
		self.actionInsertPicture = self.makeAction(self.tr('Insert &Picture'), self.insertPicture, 'Ctrl+L')
		self.actionUndo = self.makeAction(self.tr('&Undo'), self.mainWidget.undo, QKeySequence.Undo)
		self.actionRedo = self.makeAction(self.tr('&Redo'), self.mainWidget.redo, QKeySequence.Redo)
		self.actionAddNode = self.makeAction(self.tr('&Add Node'), self.mainWidget.addNode, 'Ctrl+N')
		self.actionAddSubNode = self.makeAction(self.tr('&Add SubNode'), self.mainWidget.addSubNode, 'Ctrl+Shift+N')
		self.actionMoveLeft = self.makeAction(self.tr('&Move Left'),  self.mainWidget.moveLeft, 'Ctrl+Shift+H')
		self.actionMoveDown = self.makeAction(self.tr('&Move Down'),  self.mainWidget.moveDown, 'Ctrl+Shift+J')
		self.actionMoveUp = self.makeAction(self.tr('&Move Up'),  self.mainWidget.moveUp, 'Ctrl+Shift+K')
		self.actionMoveRight = self.makeAction(self.tr('&Move Right'),  self.mainWidget.moveRight, 'Ctrl+Shift+L')
		self.actionRename = self.makeAction(self.tr('&Rename'), self.mainWidget.rename, 'F2')
		self.actionDelete = self.makeAction(self.tr('&Delete'), self.mainWidget.delete, QKeySequence.Delete)

		self.actionViewEdit = self.makeAction(self.tr('&Focus View/Edit'), self.mainWidget.switchView, 'Ctrl+T')
		self.actionTreeView = self.makeAction(self.tr('&Focus Tree/View'), self.mainWidget.switchTreeEdit, 'Ctrl+I')
		self.actionMenuBar = self.makeAction(self.tr('&Show/Hide MenuBar'), self.switchMenu, 'Ctrl+M')

		self.actionAbout = self.makeAction(self.tr('&About'), self.about)
		self.actionTutorial = self.makeAction(self.tr('&Tutorial'), self.tutorial, 'F1')

		menuBar = QMenuBar()

		menu = QMenu(self.tr('&File'))
		menu.addAction(self.actionOpen)
		menu.addAction(self.actionSave)
		menu.addAction(self.actionSaveAs)
		menu.addSeparator()
		menu.addAction(self.actionClose)
		menu.addAction(self.actionQuit)
		self.menuFile = menu
		menuBar.addMenu(menu)

		menu = QMenu(self.tr('&Edit'))
		menu.addAction(self.actionPreference)
		menu.addSeparator()
		menu.addAction(self.actionInsertCode)
		menu.addAction(self.actionInsertFile)
		menu.addAction(self.actionInsertLink)
		menu.addAction(self.actionInsertPicture)
		menu.addSeparator()
		menu.addAction(self.actionUndo)
		menu.addAction(self.actionRedo)
		menu.addSeparator()
		menu.addAction(self.actionAddNode)
		menu.addAction(self.actionAddSubNode)
		menu.addAction(self.actionMoveLeft)
		menu.addAction(self.actionMoveDown)
		menu.addAction(self.actionMoveUp)
		menu.addAction(self.actionMoveRight)
		menu.addAction(self.actionRename)
		menu.addAction(self.actionDelete)
		self.menuEdit = menu
		menuBar.addMenu(menu)

		menu = QMenu(self.tr('&View'))
		menu.addAction(self.actionViewEdit)
		menu.addAction(self.actionTreeView)
		menu.addAction(self.actionMenuBar)
		self.menuView = menu
		menuBar.addMenu(menu)

		menu = QMenu(self.tr('&Help'))
		menu.addAction(self.actionAbout)
		menu.addAction(self.actionTutorial)
		self.menuHelp = menu
		menuBar.addMenu(menu)

		self.setMenuBar(menuBar)

		self.setWindowIcon(QIcon('icon.ico'))

	def setCenter(self):
		if self.mySettings.value('MainWindow/Geometry') == None:
			self.adjustSize()
			self.move(QApplication.desktop().screen().rect().center() - self.rect().center())


	def openFile(self):
		""" open a file """
		if self.maybeSave():
			name, _ = QFileDialog.getOpenFileName(self, '', '', self.tr('ITree files (*.it)'))
			if name:
				self._openFile(name)

	def saveFile(self):
		""" save a file """
		if self.currentFileName:
			self.save(self.currentFileName)
		else:
			self.saveAsFile()

	def saveAsFile(self):
		""" save as a file """
		File = QFileDialog(self, '', '', 'ITree files (*.it)')
		File.setAcceptMode(QFileDialog.AcceptSave)
		File.setDefaultSuffix('it')
		if File.exec_() == QFileDialog.Accepted:
			self.save(File.selectedFiles()[0])

	def closeFile(self):
		""" close a file """
		if self.maybeSave():
			del self.nodeRoot
			del self.resRoot
			self.nodeRoot = INode()
			self.resRoot = IResNode()
			self.mainWidget.setRoot(self.nodeRoot)
			self.mainWidget.setResRoot(self.resRoot)
			self.resCurrentPath = '/'
			self.setCurrentName('')
			self.actionRedo.setEnabled(False)
			self.actionUndo.setEnabled(False)

	def maybeSave(self):
		""" may be sava """
		if self.isModified():
			ret = QMessageBox.warning(self, 'ITree', self.tr('The file has been modified.\nDo you want to save your changes?'),
									  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
			if ret == QMessageBox.Save:
				self.saveFile()
			elif ret == QMessageBox.Cancel:
				return False
		return True

	def preference(self):
		""" settings view """
		dialog = DialogSettings()
		dialog.apply.connect(self.settingsChanged)
		dialog.exec_()

	def insertCode(self):
		""" insert code """
		if self.mainWidget.isEditView:
			dialog = DialogInsertCode()
			if dialog.exec_() == QDialog.Accepted:
				lang = dialog.comboBox.currentText()
				title = dialog.lineEditTitle.text().replace(' ', '`')
				fold = dialog.checkBoxFold.isChecked()
				line = dialog.checkBoxLines.isChecked()
				text = dialog.textEdit.toPlainText()

				self.mainWidget.editView.insertPlainText('``` {}|title:{}|fold:{}|line:{}\n{}\n```'.format(lang, title, int(fold), int(line), text))

	def insertFile(self):
		""" insert a file """
		if self.mainWidget.isEditView:
			dialog = DialogInsertFile(self.resRoot, self.resCurrentPath)
			if dialog.exec_() == QDialog.Accepted:
				name = dialog.listView.getSelectedPath()
				infoDialog = DialogInsertLink()
				infoDialog.toolButton.hide()
				infoDialog.lineEditLink.setText(name)
				infoDialog.lineEditText.setText(os.path.basename(name))
				infoDialog.lineEditText.setFocus()
				if infoDialog.exec_() == QDialog.Accepted:
					title = infoDialog.lineEditTitle.text()
					if title:
						title = ' "' + title + '"'
					self.mainWidget.editView.insertPlainText('[{}](ifile:{}{})'.format(infoDialog.lineEditText.text(), infoDialog.lineEditLink.text(), title))

			self.resCurrentPath = dialog.path.text()
			if dialog.listView.isModified:
				self.isResModified = True
				self.updateModified()

	def insertPicture(self):
		""" insert a picture """
		if self.mainWidget.isEditView:
			dialog = DialogInsertPicture(self.resRoot)
			if dialog.exec_() == QDialog.Accepted:
				link = dialog.lineEditLink.text()
				text = dialog.lineEditText.text()
				title = dialog.lineEditTitle.text()
				width = dialog.lineEditWidth.text()
				height = dialog.lineEditHeight.text()
				size = ''
				if width and height:
					size = '|' + width + 'x' + height
				if title or size:
					title = ' "{}{}"'.format(title, size)
				self.mainWidget.editView.insertPlainText('![{}]({}{})'.format(text, link, title))

	def insertLink(self):
		""" insert a link """
		if self.mainWidget.isEditView:
			dialog = DialogInsertLink()
			dialog.lineEditText.setText(self.mainWidget.editView.textCursor().selectedText())
			if dialog.exec_() == QDialog.Accepted:
				title = dialog.lineEditTitle.text()
				if title:
					title = ' "' + title + '"'
				self.mainWidget.editView.insertPlainText('[{}]({}{})'.format(dialog.lineEditText.text(), dialog.lineEditLink.text(), title))

	def switchMenu(self):
		self.menuBar().setVisible(not self.menuBar().isVisible())

	def about(self):
		""" about application """
		QMessageBox.about(self, self.tr("About ITree"),
				r"""<center><b> ITree {} </b></center>
					<p>CopyRight &copy; 2015-2018 by {}.</p>
					<p>Email:{}</p>
					<p>Project home:<a href="https://{}">{}</a></p>
					<p>Lisence:<a href='./LICENSE'>LGPL v3.0</a></p>
					<p>
					<center><b><font color="red">Donate Me</font></b></center>
					<center>支付宝(Alipay):whiteeaglealan@gmail.com</center>
					<center><img src="donate-alipay.png" height="300" width="300"/></center>
					<center>微信(WeChat):iwtwiioi</center>
					<center><img src="donate-wechat.png" height="300" width="300"/></center>
					</p>""".format(VERSION, AUTHOR, EMAIL, PROJECTHOME, PROJECTHOME))

	def tutorial(self):
		language = self.mySettings.value('MainWindow/Language', 'default')
		if language == 'default':
			language = QLocale.system().name()
		if self.maybeSave():
			self._openFile(APP_PATH + 'tutorial/' + language + '.it')

	def clickedMenu(self, position):
		""" clicked menu """
		index = self.mainWidget.treeView.currentIndex()
		if index.isValid():
			menu = QMenu(self)
			menu.addAction(self.actionAddNode)
			menu.addAction(self.actionAddSubNode)
			menu.addAction(self.actionMoveLeft)
			menu.addAction(self.actionMoveDown)
			menu.addAction(self.actionMoveUp)
			menu.addAction(self.actionMoveRight)
			menu.addAction(self.actionRename)
			menu.addAction(self.actionDelete)
			menu.exec_(QCursor.pos())

	def isModified(self):
		""" is file modified """
		return self.mainWidget.isModified() or self.isResModified

	def updateModified(self):
		""" Modified """
		self.setWindowModified(self.isModified())

	def setCurrentName(self, name):
		self.currentFileName = name
		self.mainWidget.setModified(False)
		self.isResModified = False
		self.setWindowModified(False)
		if name:
			basename = os.path.basename(name)
		else:
			basename = self.tr('Untitled')
		self.setWindowTitle('{}[*] - ITree'.format(basename))

	def _openFile(self, filename):
		""" openfile with ITreeFile """
		if os.path.exists(filename) and open(filename, 'rb'):
			itf = ITreeFile(filename)
			x = INode()
			y = IResNode()
			if itf.open(x, y):
				self.mainWidget.setRoot(x)
				self.mainWidget.setResRoot(y)
				del self.nodeRoot
				del self.resRoot
				self.nodeRoot = x
				self.resRoot = y
				self.resCurrentPath = '/'
				self.setCurrentName(filename)
				self.actionRedo.setEnabled(False)
				self.actionUndo.setEnabled(False)
				return
		QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot open file {}'.format(filename)))

	def writeIn(self, filename):
		""" write in to file """
		itr = ITreeFile(filename)
		return itr.write(self.mainWidget.getRoot(), self.resRoot)

	def save(self, filename):
		if self.writeIn(filename):
			self.setCurrentName(filename)
		else:
			QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot write file {}'.format(filename)))

	def closeEvent(self, event):
		if self.maybeSave():
			self.saveSettings()
			event.accept()
		else:
			event.ignore()


def main():

	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	language = QSettings().value('MainWindow/Language', 'default')
	if language == 'default':
		language = QLocale.system().name()
	translator = QTranslator()
	translator.load(APP_PATH + 'i18n/' + language)
	QApplication.installTranslator(translator)
	translatorQt = QTranslator()
	translatorQt.load(APP_PATH + 'i18n/qt_' + language)
	QApplication.installTranslator(translatorQt)

	mainWindow = MainWindow()
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
