# LICENSE:LGPL v3.0

# packer

from functions import *


class NoRectangleDelegate(QStyledItemDelegate):
	def paint(self, painter, option, index):
		itemOption = QStyleOptionViewItem(option);
		if itemOption.state & QStyle.State_HasFocus:
			itemOption.state = itemOption.state ^ QStyle.State_HasFocus
		super().paint(painter, itemOption, index);


class NoRectangleListWidget(QListWidget):
	""" setting listwidget """
	def __init__(self, parent=None, padding=10):
		super().__init__(parent)

		self.myPadding = int(padding)
		self.setItemDelegate(NoRectangleDelegate())
		# self.setStyleSheet('::item { padding:10px; } ::item::selected { background: palette(Highlight); }')
		self.setStyleSheet('QListWidget::item {{ padding:{}px; padding-left:0px; }} '.format(self.myPadding))
		self.setFrameStyle(QFrame.NoFrame)

		self.currentItemChanged.connect(self.slotCurrentItemChanged)

	def sizeHint(self):
		s = QSize()
		s.setHeight(super().sizeHint().height())
		s.setWidth(self.sizeHintForColumn(0) + 2 * self.myPadding)
		return s

	def slotCurrentItemChanged(self, current, previous):
		palette = QPalette()
		if previous:
			previous.setBackground(QListWidgetItem().background())
		if current:
			current.setBackground(palette.color(QPalette.Highlight))


class LabelButton(QLabel):

	clicked = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setFocusPolicy(Qt.StrongFocus)

	def mousePressEvent(self, event):
		self.clicked.emit()


def main():
	app = QApplication(sys.argv)

	a = NoRectangleListWidget()

	for i in range(20):
		a.addItem(QListWidgetItem(str(i)))

	a.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()