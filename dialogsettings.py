# LICENSE: LGPL v3.0

# settings dialog

from functions import *
from ifont import *


class PushButtonFont(QPushButton):
	""" font button """
	def __init__(self, default=QFont(), parent=None):
		super().__init__(parent)

		default = QFont(default)
		self.connections()
		self.setMyFont(default)

	def connections(self):
		self.clicked.connect(self.open)

	def setMyFont(self, font):
		self.myFont = QFont(font)
		self.setText(QFontInfo(self.myFont).family())

	def open(self):
		dialog = DialogFont(self.myFont)
		if dialog.exec_() == QDialog.Accepted:
			self.setMyFont(dialog.lineEdit.font())


class PageAppearance(QWidget):

	LanguageDic = {
		'Default'	:	'default',
		'简体中文'	:	'zh_CN',
		'English'	:	'en_US'
	}

	def __init__(self, parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()

		layout = QVBoxLayout()
		layout.addWidget(self.widgetFont())
		layout.addWidget(self.widgetEdit())
		layout.addWidget(self.widgetOther())

		layout.addStretch()
		self.setLayout(layout)

	def saveSettings(self):
		saveFont(self.mySettings, self.pushButtonApplicationFont.myFont, 'MainWindow/')
		saveFont(self.mySettings, self.pushButtonEditFont.myFont, 'Edit/')
		saveFont(self.mySettings, self.pushButtonWebFont.myFont, 'View/')
		self.mySettings.setValue('Edit/TabStop', self.spinBoxTabSize.value())
		if self.LanguageDic[self.comboBox.currentText()] != self.mySettings.value('MainWindow/Language', 'default'):
			QMessageBox.warning(self, 'ITree', 'New language will be available by restarting ITree', QMessageBox.Ok),
		self.mySettings.setValue('MainWindow/Language', self.LanguageDic[self.comboBox.currentText()])

	def widgetFont(self):
		group = QGroupBox(self.tr('Font'))

		self.labelApplicationFont = QLabel(self.tr('Application Font'))
		self.labelEditFont = QLabel(self.tr('Edit Font'))
		self.labelWebFont = QLabel(self.tr('View Font'))

		self.pushButtonApplicationFont = PushButtonFont()
		self.pushButtonEditFont = PushButtonFont()
		self.pushButtonWebFont = PushButtonFont()

		self.pushButtonApplicationFont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.pushButtonEditFont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.pushButtonWebFont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.pushButtonApplicationFont.setMyFont(loadFont(self.mySettings, QApplication.font(), 'MainWindow/'))
		self.pushButtonEditFont.setMyFont(loadFont(self.mySettings, makeFont('YaHei Consolas Hybrid', 12, QFont.Monospace), 'Edit/'))
		self.pushButtonWebFont.setMyFont(loadFont(self.mySettings, makeFont('Helvetica', 12), 'View/'))

		layoutLeft = QVBoxLayout()
		layoutLeft.addWidget(self.labelApplicationFont)
		layoutLeft.addWidget(self.labelEditFont)
		layoutLeft.addWidget(self.labelWebFont)

		layoutRight = QVBoxLayout()
		layoutRight.addWidget(self.pushButtonApplicationFont)
		layoutRight.addWidget(self.pushButtonEditFont)
		layoutRight.addWidget(self.pushButtonWebFont)

		layout = QHBoxLayout()
		layout.addLayout(layoutLeft)
		layout.addLayout(layoutRight)

		group.setLayout(layout)

		return group

	def widgetEdit(self):
		group = QGroupBox(self.tr('Edit'))

		self.labelTabSize = QLabel(self.tr('Tab size'))
		self.spinBoxTabSize = QSpinBox()

		self.spinBoxTabSize.setRange(1, 10)
		self.spinBoxTabSize.setSingleStep(1)
		self.spinBoxTabSize.setValue(int(self.mySettings.value('Edit/TabStop', 4)))

		layout = QHBoxLayout()
		layout.addWidget(self.labelTabSize)
		layout.addStretch()
		layout.addWidget(self.spinBoxTabSize)

		group.setLayout(layout)

		return group

	def widgetOther(self):
		group = QGroupBox(self.tr('Other'))

		self.labelLanguage = QLabel(self.tr('Language'))
		self.comboBox = QComboBox()
		self.comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

		for text, lang in sorted(self.LanguageDic.items(), key=lambda x:x[0]):
			self.comboBox.addItem(text, lang)

		self.comboBox.setCurrentIndex(self.comboBox.findData(self.mySettings.value('MainWindow/Language', 'default')))

		layout = QHBoxLayout()
		layout.addWidget(self.labelLanguage)
		layout.addStretch()
		layout.addWidget(self.comboBox)

		group.setLayout(layout)

		return group


class PageNetwork(QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()

		layout = QVBoxLayout()
		layout.addWidget(self.widgetDownload())

		layout.addStretch()
		self.setLayout(layout)

	def saveSettings(self):
		self.mySettings.setValue('Network/Timeout', self.spinBoxTimeout.value())

	def widgetDownload(self):
		group = QGroupBox(self.tr('Download'))

		self.labelTimeout = QLabel(self.tr('Timeout(s)'))
		self.spinBoxTimeout = QSpinBox()

		self.spinBoxTimeout.setRange(1, 999999)
		self.spinBoxTimeout.setSingleStep(1)
		self.spinBoxTimeout.setValue(int(self.mySettings.value('Network/Timeout', 20)))

		layout = QHBoxLayout()
		layout.addWidget(self.labelTimeout)
		layout.addStretch()
		layout.addWidget(self.spinBoxTimeout)

		group.setLayout(layout)

		return group


class DialogSettings(QDialog):
	""" settings dialog """

	apply = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()
		self.listWidget = NoRectangleListWidget(self)
		self.pagesWidget = QStackedWidget(self)
		self.pushButtonOk = QPushButton(self.tr('&Ok'))
		self.pushButtonCancel = QPushButton(self.tr('&Cancel'))
		self.pushButtonApply = QPushButton(self.tr('&Apply'))
		self.listWidget.setMinimumWidth(120)

		self.initListWidget()
		self.initPagesWidget()

		scrollArea =QScrollArea()
		scrollArea.setWidget(self.pagesWidget)
		scrollArea.setWidgetResizable(True)
		scrollArea.setFrameStyle(QFrame.NoFrame)
		layoutButton = QHBoxLayout()
		layoutButton.addStretch()
		layoutButton.addWidget(self.pushButtonOk)
		layoutButton.addWidget(self.pushButtonCancel)
		layoutButton.addWidget(self.pushButtonApply)

		layoutRight = QVBoxLayout()
		layoutRight.addWidget(scrollArea)
		layoutRight.addLayout(layoutButton)
		layoutRight.setContentsMargins(0, 5, 5, 5)

		layout = QHBoxLayout()
		layout.addWidget(self.listWidget)
		layout.addLayout(layoutRight)

		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)
		self.setMinimumSize(500, 400)
		self.setWindowTitle(self.tr('Preference'))
		self.adjustSize()
		self.connections()
		self.loadSettings()

	def loadSettings(self):
		self.mySettings.beginGroup('DialogSettings')
		self.restoreGeometry(self.mySettings.value('Geometry'))
		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogSettings')
		self.mySettings.setValue('Geometry', self.saveGeometry())
		self.mySettings.endGroup()

	def connections(self):
		self.pushButtonApply.clicked.connect(self.apply)
		self.pushButtonOk.clicked.connect(self.accept)
		self.pushButtonCancel.clicked.connect(self.reject)

		self.apply.connect(self.slotApply)

	def initListWidget(self):
		self.PagesName = [self.tr('Appearance'),
						  self.tr('Network')]

		# for i in range(20):
		#	self.PagesName.append(str(i))

		for name in self.PagesName:
			item = QListWidgetItem(name, self.listWidget)
			item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			item.setTextAlignment(Qt.AlignCenter)

		# self.listWidget.setMinimumWidth(self.listWidget.sizeHintForColumn(0))
		self.listWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.listWidget.setCurrentRow(0)
		self.listWidget.currentItemChanged.connect(self.indexChanged)

	def initPagesWidget(self):
		self.Pages = [PageAppearance(),
					  PageNetwork()]

		# for i in range(20):
		#	self.Pages.append(QPlainTextEdit())

		for page in self.Pages:
			self.pagesWidget.addWidget(page)

		self.pagesWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.pagesWidget.setCurrentIndex(0)

	def indexChanged(self, current, previous):
		if current:
			self.pagesWidget.setCurrentIndex(self.listWidget.row(current))

	def slotApply(self):
		self.listWidget.setFont(self.Pages[0].pushButtonApplicationFont.myFont)
		for page in self.Pages:
			page.saveSettings()

	def accept(self):
		self.apply.emit()
		self.saveSettings()
		super().accept()

	def reject(self):
		self.saveSettings()
		super().reject()


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	mainWindow = DialogSettings()
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
