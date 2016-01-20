# LICENSE:LGPL v3.0

# MainWidget

from functions import *
from ifont import *
from itreefile import INode, IResNode
from widgetTreeView import *
from widgetTextEdit import *
from widgetWebView import *


class UndoCommand(QUndoCommand):
	"""
	flag (data)
	1 - textEdit
	2 - current index (current, previous, 0)/(current, previous, 1)
	3 - treeNode insert (node, row, parent)/None
	4 - treeNode delete (row, parent)/(node, row, parent)
	5 - treeNode rename (index, oldname, newname)
	6 - treeNode move ()
	"""

	def __init__(self, data, flag, parent):
		""" init """
		super().__init__()
		self.data = data
		self.flag = flag
		self.main = parent

	def redo(self):
		""" redo """
		if self.flag == 1:
			self.main.editView.redo()
		elif self.flag == 2:
			if self.data[2] == 0:
				self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				self.main.editView.document().undoCommandAdded.disconnect(self.main.commandEditChanged)
				current, previous, _ = self.data
				self.main.treeView.setCurrentIndex(current)
				if previous.isValid():
					self.main.model.updateData(previous, self.main.editView.toPlainText(), 2)
				self.main.treeView.indexChanged.connect(self.main.indexChanged)
				self.main.editView.document().undoCommandAdded.connect(self.main.commandEditChanged)
		elif self.flag == 3:
			if self.data:
				# self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				node, row, parent = self.data
				if len(self.main.model.root) == 0:
					self.main.editView.setReadOnly(False)
				self.main.model.insert(node, row, parent)
				# self.main.treeView.indexChanged.connect(self.main.indexChanged)
		elif self.flag == 4:
			if len(self.data) == 2:
				self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				row, parent = self.data
				self.main.model.delete(self.main.model.index(row, 0, parent))
				if len(self.main.model.root) == 0:
					self.main.editView.setReadOnly(True)
				self.main.treeView.indexChanged.connect(self.main.indexChanged)
		elif self.flag == 5:
			self.main.model.updateData(self.data[0], self.data[2], 1)

	def undo(self):
		""" undo """
		if self.flag == 1:
			self.main.editView.undo()
		elif self.flag == 2:
			if self.data[2] == 1:
				self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				self.main.editView.document().undoCommandAdded.disconnect(self.main.commandEditChanged)
				previous, current, _ = self.data
				if current.isValid():
					self.main.treeView.setCurrentIndex(current)
				if previous.isValid():
					self.main.model.updateData(previous, self.main.editView.toPlainText(), 2)
				self.main.treeView.indexChanged.connect(self.main.indexChanged)
				self.main.editView.document().undoCommandAdded.connect(self.main.commandEditChanged)
		elif self.flag == 3:
			if self.data:
				self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				node, row, parent = self.data
				self.main.model.delete(self.main.model.index(row, 0, parent))
				if len(self.main.model.root) == 0:
					self.main.editView.setReadOnly(True)
				self.main.treeView.indexChanged.connect(self.main.indexChanged)
		elif self.flag == 4:
			if len(self.data) == 3:
				self.main.treeView.indexChanged.disconnect(self.main.indexChanged)
				node, row, parent = self.data
				if len(self.main.model.root) == 0:
					self.main.editView.setReadOnly(False)
				self.main.model.insert(node, row, parent)
				self.main.treeView.indexChanged.connect(self.main.indexChanged)
		elif self.flag == 5:
			self.main.model.updateData(self.data[0], self.data[1], 1)


class UndoStack(QUndoStack):
	""" custom undostack """

	def __init__(self, parent=None):
		super().__init__(parent)
		self.pos = -1
		self.modified = False

	def clear(self):
		self.pos = -1
		self.modified = False
		super().clear()

	def undo(self):
		super().undo()

	def redo(self):
		super().redo()

	def getCurrentPos(self):
		""" get current pos (except index changed) """
		pos = self.index() - 1
		if pos >= 0 and self.command(pos).flag == 2 and self.command(pos).data[2] == 1:
			pos -= 1
			while self.command(pos).flag != 2:
				pos -= 1
			pos -= 1
		return pos

	def setModified(self, modified):
		if modified == False:
			self.pos = self.getCurrentPos()
			self.modified = False

	def push(self, cmd):
		if not self.modified and self.index() <= self.pos:
			self.modified = True
		super().push(cmd)

	def isModified(self):
		return self.modified or self.getCurrentPos() != self.pos


class MainWidget(QWidget):

	contentsChanged = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)

		self.mySettings = QSettings()
		self.markdown = IMarkdown()
		self.model = TreeViewModel(TreeNode(), self)
		self.treeView = TreeView(self)
		self.editView = TextEdit(self)
		self.webView = WebView(IResNode(), self)
		self.splitter = QSplitter(self)
		self.undoStack = UndoStack(self)
		self.rightWidget = QStackedWidget(self)
		self.htmlHeader = ''
		self.htmlFooter = ''
		self.isEditView = True
		self.viewPreviousIndex = QModelIndex()
		self.tempList = []

		self.rightWidget.addWidget(self.editView)
		self.rightWidget.addWidget(self.webView)
		self.rightWidget.setCurrentIndex(0)

		self.treeView.setMinimumWidth(1)
		self.rightWidget.setMinimumWidth(1)
		self.splitter.addWidget(self.treeView)
		self.splitter.addWidget(self.rightWidget)
		self.splitter.setHandleWidth(5)
		self.splitter.setContentsMargins(0, 0, 0, 0)

		self.loadSettings()
		self.connections()
		self.loadInternalJavaScript()
		self.setTree()

		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.splitter)
		self.setLayout(layout)

	def connections(self):
		self.treeView.indexChanged.connect(self.indexChanged)
		self.editView.undoSignal.connect(self.undo)
		self.editView.redoSignal.connect(self.redo)
		self.editView.document().undoCommandAdded.connect(self.commandEditChanged)
		self.editView.document().contentsChanged.connect(self.contentsChanged)
		self.webView.linkRenderer.needTempFile.connect(self.makeResTemp)

	def loadSettings(self):
		self.mySettings.beginGroup('MainWidget')
		self.splitter.restoreState(self.mySettings.value('Splitter/State'))
		self.mySettings.endGroup()
		self.editView.loadSettings()
		self.webView.loadSettings()

	def saveSettings(self):
		self.mySettings.beginGroup('MainWidget')
		self.mySettings.setValue('Splitter/State', self.splitter.saveState())
		self.mySettings.endGroup()
		self.mySettings.setValue('View/Zoom', self.webView.zoom)

	def wrapper(self, html):
		""" add something """
		# fil = open('a.html', 'w')
		# fil.write(self.htmlHeader + self.markdown(html) + self.htmlFooter)
		# fil.close()
		# return self.markdown(html)
		return self.htmlHeader + self.markdown(html) + self.htmlFooter

	def loadInternalJavaScript(self):
		""" load JavaScript """
		self.htmlHeader += r'''
<script type="text/javascript" src="{path}res/MathJax/MathJax.js?config=TeX-AMS_HTML"></script>
<script type="text/javascript">MathJax.Hub.Config({{tex2jax: {{inlineMath: [ ['$','$'], ['\\(','\\)'] ]}}}});</script>
<script type="text/javascript" src="{path}res/SyntaxHighlighter/scripts/shCore.js"></script>
<script type="text/javascript" src="{path}res/SyntaxHighlighter/scripts/shAutoloader.js" ></script>
<link type="text/css" rel="stylesheet" href="{path}res/SyntaxHighlighter/styles/shCore.css"/>
<link type="text/css" rel="stylesheet" href="{path}res/SyntaxHighlighter/styles/shThemeDefault.css"/>
<link type="text/css" rel="stylesheet" href="{path}res/default.css"/>
'''.format(path=APP_PATH)

		self.htmlFooter += r'''
<script type="text/javascript">
function rpath(name){{return name.replace('@', '{path}res/SyntaxHighlighter/scripts/');}}
SyntaxHighlighter.autoloader(
[ 'applescript',					rpath('@shBrushAppleScript.js') ],
[ 'actionscript3', 'as3',			rpath('@shBrushAS3.js') ],
[ 'bash', 'shell',					rpath('@shBrushBash.js') ],
[ 'coldfusion', 'cf',				rpath('@shBrushColdFusion.js') ],
[ 'cpp', 'c',						rpath('@shBrushCpp.js') ],
[ 'c#', 'c-sharp', 'csharp',		rpath('@shBrushCSharp.js') ],
[ 'css',							rpath('@shBrushCss.js') ],
[ 'delphi', 'pascal',				rpath('@shBrushDelphi.js') ],
[ 'diff', 'patch', 'pas',			rpath('@shBrushDiff.js') ],
[ 'erl', 'erlang',					rpath('@shBrushErlang.js') ],
[ 'groovy',							rpath('@shBrushGroovy.js') ],
[ 'java',							rpath('@shBrushJava.js') ],
[ 'jfx', 'javafx',					rpath('@shBrushJavaFX.js') ],
[ 'js', 'javascript', 'jscript',	rpath('@shBrushJScript.js') ],
[ 'perl', 'pl',						rpath('@shBrushPerl.js') ],
[ 'php',							rpath('@shBrushPhp.js') ],
[ 'text', 'plain',					rpath('@shBrushPlain.js') ],
[ 'py', 'python',					rpath('@shBrushPython.js') ],
[ 'ruby', 'rails', 'ror', 'rb',		rpath('@shBrushRuby.js') ],
[ 'sass', 'scss',					rpath('@shBrushSass.js') ],
[ 'scala',							rpath('@shBrushScala.js') ],
[ 'sql',							rpath('@shBrushSql.js') ],
[ 'vb', 'vbnet',					rpath('@shBrushVb.js') ],
[ 'xml', 'xslt', 'html', 'htm',		rpath('@shBrushXml.js') ]
);
SyntaxHighlighter.all();
</script>
'''.format(path=APP_PATH)

	def setTree(self):
		""" treeView settings """
		# self.treeView.setFocusProxy(self.editView)
		self.treeView.setModel(self.model)
		self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.treeView.setCurrentIndex(QModelIndex())
		self.treeView.horizontalScrollBar().hide()
		# self.treeView.setDragDropMode(self.treeView.DragDrop)
		# self.treeView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
		# self.treeView.setSelectionBehavior(QAbstractItemView.SelectItems)
		# self.treeView.header().setResizeMode(QHeaderView.ResizeToContents)
		# self.treeView.header().setStretchLastSection(False)
		# self.treeView.header().resizeSection(0,50)
		# self.treeView.setAutoScroll(True)
		# self.treeView.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		# self.treeView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.treeView.header().hide()
		# self.editView.setReadOnly(True) # here is a bug.
		if len(self.model.root):
			self.editView.setReadOnly(False)
			self.treeView.indexChanged.disconnect(self.indexChanged)
			index = self.model.index(0, 0)
			self.treeView.setCurrentIndex(index)
			self.treeView.indexChanged.connect(self.indexChanged)
			self.editView.setPlainText(self.model.getData(index, 2))

	def makeINode(self, y):
		""" make INode """
		x = INode(y.name, y.text)
		for i in range(len(y)):
			x.add(self.makeINode(y.child[i]))
		return x

	def makeTreeNode(self, y, parent=None):
		""" make TreeNode """
		x = TreeNode(y.name, y.text, parent)
		for i in range(y.len()):
			x.append(self.makeTreeNode(y.at(i), x))
		return x

	def isModified(self):
		return self.undoStack.isModified() or self.editView.document().isModified()

	def setModified(self, modified):
		if modified == False:
			self.undoStack.setModified(False)
			self.editView.document().setModified(False)

	def commandEditChanged(self):
		""" push into undo/redo stack with currentIndex """
		self.undoStack.push(UndoCommand(None, 1, self))

	def indexChanged(self, current, previous):
		""" changed index """
		if self.isEditView:
			if self.undoStack.index() and self.undoStack.command(self.undoStack.index() - 1).flag == 2:
				cmd = self.undoStack.command(self.undoStack.index() - 1)
				previous = cmd.data[1]
				cmd.data = (cmd.data[0], QModelIndex(), cmd.data[2])
				self.undo()
			if previous != current:
				self.editView.document().contentsChanged.disconnect(self.contentsChanged)
				self.undoStack.push(UndoCommand((current, previous, 0), 2, self))
				if current.isValid():
					self.editView.changeText(self.model.getData(current, 2))
				else:
					self.editView.changeText('')
				self.undoStack.push(UndoCommand((current, previous, 1), 2, self))
				self.editView.document().contentsChanged.connect(self.contentsChanged)
				if not self.undoStack.isModified():
					self.editView.document().setModified(False)
		else:
			if current.isValid():
				self.webView.setHtml(self.wrapper(self.model.getData(current, 2)))
			else:
				self.webView.setHtml('')

	def addNode(self):
		""" add a node under it """
		if not self.isEditView:
			return
		index = self.treeView.currentIndex()
		parent = QModelIndex()
		if index.isValid():
			parent = self.model.parent(index)
		row = index.row() + 1
		self.undoStack.push(UndoCommand((TreeNode(self.tr('Unknown'), '', None), row, parent), 3, self))
		self.treeView.setCurrentIndex(self.model.index(row, 0, parent))
		self.undoStack.push(UndoCommand(None, 3, self))
		self.contentsChanged.emit()

	def addSubNode(self):
		""" add a node in it """
		if not self.isEditView:
			return
		index = self.treeView.currentIndex()
		self.treeView.expand(index)
		self.undoStack.push(UndoCommand((TreeNode(self.tr('Unknown'), '', None), self.model.rowCount(index), index), 3, self))
		self.treeView.setCurrentIndex(self.model.index(self.model.rowCount(index) - 1, 0, index))
		self.undoStack.push(UndoCommand(None, 3, self))
		self.contentsChanged.emit()

	def rename(self):
		""" rename currentIndex """
		if not self.isEditView:
			return
		index = self.treeView.currentIndex()
		if index.isValid():
			oldName = self.model.getData(index, 1)
			name, ok = QInputDialog.getText(self, self.tr("Rename"), self.tr('Input a string'), QLineEdit.Normal, oldName, Qt.WindowOkButtonHint)
			if ok and oldName != name:
				self.undoStack.push(UndoCommand((index, oldName, name), 5, self))
				self.contentsChanged.emit()

	def delete(self):
		""" delete cureentIndex """
		if not self.isEditView:
			return
		index = self.treeView.currentIndex()
		if index.isValid():
			node = self.model.indexOf(index)
			row = index.row()
			parent = self.model.parent(index)
			self.undoStack.push(UndoCommand((row, parent), 4, self))
			self.indexChanged(self.treeView.currentIndex(), index)
			self.undoStack.push(UndoCommand((node, row, parent), 4, self))
			self.contentsChanged.emit()

	def undo(self, isFirst=True):
		""" undo """
		if self.isEditView:
			index = self.undoStack.index()
			if index:
				cmd = self.undoStack.command(index - 1)
				data, flag = cmd.data, cmd.flag
				if flag == 1:
					self.undoStack.undo()
				elif flag == 2:
					if data[2] == 1:
						self.editView.document().contentsChanged.disconnect(self.contentsChanged)
						self.undoStack.undo()
						if self.undoStack.command(index - 2).flag == 1:
							self.undoStack.undo()
							self.editView.moveToStart()
						self.undoStack.undo()
						self.editView.document().contentsChanged.connect(self.contentsChanged)
						if not self.undoStack.isModified():
							self.editView.document().setModified(False)
				elif flag == 3:
					if not data:
						self.undoStack.undo()
						self.undo(False)
						self.undoStack.undo()
				elif flag == 4:
					self.undoStack.undo()
					self.undo(False)
					self.undoStack.undo()
				elif flag == 5:
					self.undoStack.undo()
				elif flag == 6:
					self.undoStack.undo()
					self.undo(False)
					self.undo(False)
					self.undoStack.undo()

				if isFirst:
					self.contentsChanged.emit()

	def redo(self, isFirst=True):
		""" redo """
		if self.isEditView:
			index = self.undoStack.index()
			if index < self.undoStack.count():
				cmd = self.undoStack.command(index)
				data, flag = cmd.data, cmd.flag
				if flag == 1:
					self.undoStack.redo()
				elif flag == 2:
					if data[2] == 0:
						self.editView.document().contentsChanged.disconnect(self.contentsChanged)
						self.undoStack.redo()
						if self.undoStack.command(index + 1).flag == 1:
							self.undoStack.redo()
							self.editView.moveToStart()
						self.undoStack.redo()
						self.editView.document().contentsChanged.connect(self.contentsChanged)
						if not self.undoStack.isModified():
							self.editView.document().setModified(False)
				elif flag == 3:
					if data:
						self.undoStack.redo()
						self.redo(False)
						self.undoStack.redo()
				elif flag == 4:
					self.undoStack.redo()
					self.redo(False)
					self.undoStack.redo()
				elif flag == 5:
					self.undoStack.redo()
				elif flag == 6:
					self.undoStack.redo()
					self.redo()
					self.redo()
					self.undoStack.redo()

				if isFirst:
					self.contentsChanged.emit()

	def move(self, index, insertParent, insertRow):
		node = self.model.indexOf(index)
		row = index.row()
		parent = self.model.parent(index)
		self.undoStack.push(UndoCommand(None, 6, self))

		self.undoStack.push(UndoCommand((row, parent), 4, self))
		self.indexChanged(self.treeView.currentIndex(), index)
		self.undoStack.push(UndoCommand((node, row, parent), 4, self))

		if len(insertParent) == 1:
			insertParent = insertParent[0]
		else:
			insertParent = self.model.index(insertParent[0], 0, insertParent[1])
		self.undoStack.push(UndoCommand((node, insertRow, insertParent), 3, self))
		self.treeView.setCurrentIndex(self.model.index(insertRow, 0, insertParent))
		self.undoStack.push(UndoCommand(None, 3, self))

		self.undoStack.push(UndoCommand(None, 6, self))
		self.contentsChanged.emit()

	def moveLeft(self):
		if self.isEditView:
			index = self.treeView.currentIndex()
			if index.isValid():
				parent = self.model.parent(index)
				if parent.isValid():
					self.move(index, [self.model.parent(parent)], parent.row())

	def moveDown(self):
		if self.isEditView:
			index = self.treeView.currentIndex()
			if index.isValid():
				parent = self.model.parent(index)
				row = -1
				if self.model.rowCount(parent) - 1 == index.row():
					if parent.isValid():
						row = parent.row() + 1
						parent = self.model.parent(parent)
					else:
						parent = None
				else:
					row = index.row() + 1
				if parent != None:
					self.move(index, [parent], row)

	def moveUp(self):
		if self.isEditView:
			index = self.treeView.currentIndex()
			if index.isValid():
				parent = None
				row = -1
				parent = self.model.parent(index)
				if index.row() == 0:
					if parent.isValid():
						row = parent.row()
						parent = self.model.parent(parent)
					else:
						parent = None
				else:
					row = index.row() - 1
				if parent != None:
					self.move(index, [parent], row)

	def moveRight(self):
		if self.isEditView:
			index = self.treeView.currentIndex()
			if index.isValid():
				parent = self.model.parent(index)
				if self.model.rowCount(parent) - 1 != index.row():
					self.move(index, [index.row(), parent], 0)

	def switchView(self):
		""" switch Edit/WebView """
		if self.isEditView:
			self.isEditView = False
			self.webView.setHtml(self.wrapper(self.editView.toPlainText()))
			index = self.treeView.currentIndex()
			if index.isValid():
				self.model.updateData(index, self.editView.toPlainText(), 2)
			self.rightWidget.setCurrentIndex(1)
			self.viewPreviousIndex = index
		else:
			self.isEditView = True
			self.rightWidget.setCurrentIndex(0)
			index = self.treeView.currentIndex()
			if self.viewPreviousIndex != index:
				self.indexChanged(index, self.viewPreviousIndex)

	def switchTreeEdit(self):
		if self.treeView.hasFocus():
			if self.isEditView and not self.editView.isReadOnly():
				self.editView.setFocus()
			elif not self.isEditView:
				self.webView.setFocus()
		else:
			self.treeView.setFocus()

	def makeResTemp(self, temp, path):
		now = self.webView.imageRenderer.root
		try:
			if path:
				path = path.split('/')
				if path and path[0] == '':
					path = path[1:]
				if path and path[-1] == '':
					path = path[:-1]
				for name in path:
					pos = now.findName(name)
					if pos == -1:
						return
					now = now.at(pos)
				if now.isFile():
					now.data().write(temp.fileName())
					self.tempList.append(temp)
		except Exception:
			pass

	def setRoot(self, root):
		root = self.makeTreeNode(root)
		self.model = TreeViewModel(root)
		self.undoStack.clear()
		self.editView.clear()
		self.setTree()
		self.viewPreviousIndex = QModelIndex()
		if not self.isEditView:
			self.switchView()

	def setResRoot(self, root):
		self.webView.setRoot(root)

	def getRoot(self):
		index = self.treeView.currentIndex()
		if index.isValid():
			self.model.updateData(index, self.editView.toPlainText(), 2)
		return self.makeINode(self.model.root)


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()