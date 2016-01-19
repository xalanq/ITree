# LICENSE: LGPL v3.0

# font stuff

from functions import *
from widgetsOther import *


def saveFont(settings, font, addtion=''):
	settings.setValue(addtion + 'Font/Family', QFontInfo(font).family())
	settings.setValue(addtion + 'Font/PointSize', font.pointSize())

def loadFont(settings, default, addition=''):
	font = QFont(default)
	font.setFamily(settings.value(addition + 'Font/Family', default.family()))
	font.setPointSize(int(settings.value(addition + 'Font/PointSize', default.pointSize())))
	return font

def makeFontStyleHint(font, styleHint):
	if styleHint != None:
		font.setStyleHint(styleHint)
		if styleHint == QFont.Monospace:
			font.setFixedPitch(True)
	return font

def makeFont(family, pointSize, styleHint=None):
	font = QFont(family, pointSize)
	makeFontStyleHint(font, styleHint)
	return font


class DialogFont(QDialog):
	""" font dialog """

	def __init__(self, default, parent=None):
		super().__init__(parent)

		default = QFont(default)
		self.mySettings = QSettings()
		self.listWidget = NoRectangleListWidget(self)
		self.slider = QSlider(Qt.Horizontal, self)
		self.spinBox = QSpinBox(self)
		self.lineEdit = QLineEdit(self)
		self.userFont = default

		self.slider.setRange(6, 72)
		self.slider.setSingleStep(1)
		self.spinBox.setRange(6, 72)
		self.spinBox.setSingleStep(1)
		self.slider.setValue(default.pointSize())
		self.spinBox.setValue(default.pointSize())
		self.lineEdit.setFont(self.userFont)

		layoutDown = QHBoxLayout()
		layoutDown.addWidget(self.slider)
		layoutDown.addWidget(self.spinBox)

		layout = QVBoxLayout()
		layout.addWidget(self.listWidget)
		layout.addWidget(self.lineEdit)
		layout.addLayout(layoutDown)

		self.setLayout(layout)

		self.loadSettings()
		self.initListWidget()
		self.connections()

		self.setWindowTitle(self.tr('Font'))
		self.setMinimumSize(400, 300)

	def loadSettings(self):
		self.mySettings.beginGroup('DialogFont')

		self.restoreGeometry(self.mySettings.value('Geometry'))
		self.lineEdit.setText(self.mySettings.value('DefaultText', 'abcdefg ABCDEFG 0123456789'))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogFont')

		self.mySettings.setValue('Geometry', self.saveGeometry())
		self.mySettings.setValue('DefaultText', self.lineEdit.text())

		self.mySettings.endGroup()

	def connections(self):
		self.spinBox.valueChanged[int].connect(self.slider.setValue)
		self.slider.valueChanged[int].connect(self.spinBox.setValue)
		self.slider.valueChanged[int].connect(self.sizeChanged)
		self.listWidget.currentItemChanged.connect(self.itemChanged)

	def initListWidget(self):
		for name in QFontDatabase().families():
			item = QListWidgetItem(name, self.listWidget)
			item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			item.setTextAlignment(Qt.AlignCenter)

			if name == QFontInfo(self.userFont).family():
				self.listWidget.setCurrentItem(item)

	def itemChanged(self, current, previous):
		self.userFont.setFamily(current.text())
		self.lineEdit.setFont(self.userFont)

	def sizeChanged(self, size):
		self.userFont.setPointSize(size)
		self.lineEdit.setFont(self.userFont)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
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

	mainWindow = DialogFont(QFont())
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
