# LICENSE: LGPL v3.0

# insert code dialog

from functions import *
from ui_dialoginsertcode import Ui_DialogInsertCode
from ifont import *

class DialogInsertCode(QDialog, Ui_DialogInsertCode):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)

		self.mySettings = QSettings()

		self.loadSettings()
		self.connections()

	def setupUi(self, DialogInsertCode):
		super().setupUi(DialogInsertCode)
		self.textEdit.setFocus()

	def connections(self):
		self.pushButtonOpen.clicked.connect(self.open)
		QShortcut(QKeySequence(Qt.ALT + Qt.Key_T), self, self.lineEditTitle.setFocus)

	def loadSettings(self):
		self.mySettings.beginGroup('DialogInsertCode')

		self.restoreGeometry(self.mySettings.value('Geometry'))

		self.comboBox.setCurrentIndex(int(self.mySettings.value('ComboBox/CurrentIndex', 17)))
		self.checkBoxFold.setChecked(self.mySettings.value('CheckBoxFold/Checked', 'false') == 'true')
		self.checkBoxLines.setChecked(self.mySettings.value('CheckBoxLines/Checked', 'false') == 'true')

		self.mySettings.endGroup()

		self.mySettings.beginGroup('Edit')

		tabStop = int(self.mySettings.value('TabStop', 4))
		font = loadFont(self.mySettings, makeFont('YaHei consolas hybrid', 12, QFont.Monospace))
		font.setStyleHint(QFont.Monospace)
		font.setFixedPitch(True)
		self.textEdit.setFont(font)
		self.textEdit.setTabStopWidth(tabStop * QFontMetrics(font).width(' '))

		self.mySettings.endGroup()

	def saveSettings(self):
		self.mySettings.beginGroup('DialogInsertCode')

		self.mySettings.setValue('Geometry', self.saveGeometry())
		self.mySettings.setValue('ComboBox/CurrentIndex', self.comboBox.currentIndex())
		self.mySettings.setValue('CheckBoxFold/Checked', self.checkBoxFold.isChecked())
		self.mySettings.setValue('CheckBoxLines/Checked', self.checkBoxLines.isChecked())

		self.mySettings.endGroup()

	def open(self):
		name, _ = QFileDialog.getOpenFileName(self, '', '')
		if name:
			file = QFile(name)
			if file.open(QIODevice.ReadOnly):
				self.textEdit.setPlainText(QTextStream(file).readAll())
				self.lineEditTitle.setText(os.path.basename(name))
			else:
				QMessageBox.warning(self, self.tr('Error'), self.tr('Cannot open file {}'.format(name)))
		self.textEdit.setFocus();

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
			if event.modifiers() & Qt.ControlModifier:
				self.accept()
		else:
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

	mainWindow = DialogInsertCode()
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()