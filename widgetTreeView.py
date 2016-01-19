# LICENSE:LGPL v3.0

# TreeView

from functions import *
from ifont import *


class TreeNode:
	""" ************************************************* node ************************************************* """
	def __init__(self, name='', text='', parent=None):
		""" __init__ """
		self.name = name
		self.text = text
		self.parent = parent
		self.child = []

	def __len__(self):
		""" set len() """
		return len(self.child)

	def row(self):
		""" get row """
		if self.parent != None:
			return self.parent.child.index(self)
		assert False
		return None

	def at(self, row):
		""" select node at row """
		if 0 <= row < len(self.child):
			return self.child[row]
		return None

	def append(self, node):
		""" add a node at back """
		self.child.append(node)

	def insert(self, node, row):
		""" insert node at row """
		assert 0 <= row <= len(self.child)
		self.child.insert(row, node)

	def delete(self, row):
		""" delete node at row """
		assert 0 <= row < len(self.child)
		return self.child.pop(row)


class TreeViewModel(QAbstractItemModel):
	""" ************************************************* custom mode ************************************************* """

	def __init__(self, root, parent=None):
		""" __init__ """
		super().__init__(parent)

		self.root = root

	def indexOf(self, index):
		""" get node by index """
		if index.isValid():
			return index.internalPointer()
		return self.root

	def columnCount(self, index):
		""" columns """
		return 1

	def rowCount(self, index):
		""" rows """
		return len(self.indexOf(index))

	def hasChildren(self, index):
		""" check if index has children """
		return self.rowCount(index) != 0

	def flags(self, index):
		""" flags : enable, selectable, drag, drop """
		return	Qt.ItemIsEnabled | \
				Qt.ItemIsSelectable | \
				Qt.ItemIsDragEnabled | \
				Qt.ItemIsDropEnabled

	def data(self, index, role):
		""" get the data with role """
		if not index.isValid():
			return None
		node = self.indexOf(index)
		if role == Qt.DisplayRole:
			return node.name
		return None

	def setData(self, index, value, role=Qt.EditRole):
		""" set Data """
		if not index.isValid():
			return False
		node = self.indexOf(index)
		if role == Qt.EditRole:
			node.name = value
		self.dataChanged.emit(index, index)
		return True

	def getData(self, index, flag):
		""" get data of index - flag :
			1 - name
			2 - text
		"""
		node = self.indexOf(index)
		assert node != self.root
		if flag == 1:
			return node.name
		elif flag == 2:
			return node.text
		return None

	def updateData(self, index, value, flag):
		""" update data of index - flag :
			1 - name
			2 - text
		"""
		node = self.indexOf(index)
		assert node != self.root
		if flag == 1:
			node.name = value
		elif flag == 2:
			node.text = value
		self.dataChanged.emit(index, index)

	def index(self, row, column, parent=QModelIndex()):
		""" get index """
		ret = QModelIndex()
		node = self.indexOf(parent)
		child = node.at(row)
		if child != None:
			ret = self.createIndex(row, column, child)
		return ret

	def parent(self, index):
		""" index of parent """
		node = self.indexOf(index)
		assert node != None and node != self.root
		ret = QModelIndex()
		node = node.parent
		if node != None and node.parent != None:
			ret = self.createIndex(node.row(), 0, node)
		return ret

	def delete(self, index):
		""" delete one node from index """
		if index.isValid():
			parentIndex = self.parent(index)
			node = self.indexOf(index)
			parent = self.indexOf(parentIndex)
			row = node.row()
			self.beginRemoveRows(parentIndex, row, row)
			item = parent.delete(row)
			self.endRemoveRows()

	def insert(self, data, row, parent=QModelIndex()):
		""" insert a node at row """
		self.beginInsertRows(parent, row, row)
		node = self.indexOf(parent)
		data.parent = node
		node.insert(data, row)
		self.endInsertRows()
		return self.index(row, 0, parent)


class TreeView(QTreeView):
	""" ************************************************* tree view ************************************************* """
	indexChanged = Signal(QModelIndex, QModelIndex)

	def __init__(self, parent=None):
		""" init """
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.setFrameStyle(QFrame.NoFrame)

	def mouseDoubleClickEvent(self, e):
		pass

	def currentChanged(self, current, previous):
		""" item changed """
		super().currentChanged(current, previous)
		self.indexChanged.emit(current, previous)

	def sizeHint(self):
		return QSize(150, super().sizeHint().height())

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_H:
			event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Left, event.modifiers(), event.text(), event.isAutoRepeat(), event.count())
		elif event.key() == Qt.Key_J:
			event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Down, event.modifiers(), event.text(), event.isAutoRepeat(), event.count())
		elif event.key() == Qt.Key_K:
			event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Up, event.modifiers(), event.text(), event.isAutoRepeat(), event.count())
		elif event.key() == Qt.Key_L:
			event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Right, event.modifiers(), event.text(), event.isAutoRepeat(), event.count())
		super().keyPressEvent(event)


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()