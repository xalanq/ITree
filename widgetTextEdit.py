# LICENSE:LGPL v3.0

# TextEdit

from functions import *
from ifont import *


class TextEdit(QPlainTextEdit):
	""" ************************************************* text edit ************************************************* """
	undoSignal = Signal()
	redoSignal = Signal()

	def __init__(self, parent=None):
		""" init """
		super().__init__(parent)

		self.tabStop = 4
		self.mySettings = QSettings()

		self.loadSettings()
		self.setFrameStyle(QFrame.NoFrame)

	def loadSettings(self):
		self.mySettings.beginGroup('Edit')

		self.tabStop = int(self.mySettings.value('TabStop', 4))

		self.setFont(loadFont(self.mySettings, makeFont('YaHei consolas hybrid', 12, QFont.Monospace)))

		self.mySettings.endGroup()

	def setFont(self, font):
		super().setFont(font)
		self.setTabStopWidth(self.tabStop * QFontMetrics(font).width(' '))

	def changeText(self, text):
		""" change text without clearing undo/redo history """
		cur = QTextCursor(self.document())
		cur.select(QTextCursor.Document)
		cur.insertText(text)
		cur.movePosition(QTextCursor.Start)
		self.setTextCursor(cur)

	def moveToStart(self):
		cur = QTextCursor(self.document())
		cur.movePosition(QTextCursor.Start)
		self.setTextCursor(cur)

	def keyPressEvent(self, event):
		""" reset key ctrl+z, ctrl+shift+z """
		mod = event.modifiers()
		key = event.key()
		if (mod & Qt.ControlModifier) and (mod & Qt.ShiftModifier) and (key == Qt.Key_Z):
			self.redoSignal.emit()
		elif (mod & Qt.ControlModifier) and (key == Qt.Key_Z):
			self.undoSignal.emit()
		else:
			super().keyPressEvent(event)

	def setReadOnly(self, Flag):
		''' bug here '''
		# super().setReadOnly(Flag)
		pass


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()