# LICENSE:LGPL v3.0

# WebView

from functions import *
from ifont import *
from dialoginsertpicture import DialogInsertPicture


class WebLinkRenderer(QObject):
	""" a link render """
	needTempFile = Signal(QTemporaryFile, str)

	def __init__(self, parent=None):
		super().__init__(parent)

	def openLink(self, link):
		try:
			if QDesktopServices.openUrl(link):
				return True
		except Exception:
			pass
		return False

	@Slot(QWebElement)
	def processing(self, item):

		link = item.attribute('href')
		temp = None

		if link.startswith('ifile:'):
			link = link[6:]
			try:
				temp = QTemporaryFile(QDir.tempPath() + '/ITree-XXXXXX-{}'.format(os.path.basename(link)))
				if temp.open():
					self.needTempFile.emit(temp, link)
					link = temp.fileName()
			except Exception:
				return
		if not self.openLink(QUrl.fromUserInput(link)):
			if os.path.exists(link):
				self.openLink(QUrl.fromUserInput(QFileInfo(link).absoluteFilePath()))


class WebImageRenderer(QObject):
	""" a image render """

	def __init__(self, parent=None):
		super().__init__(parent)
		self.pixmaps = {}
		self.now = None
		self.root = None

	def clear(self):
		self.pixmaps.clear()

	@Slot(QWebElement)
	def processing(self, item):
		link = item.attribute('link')

		pic = None
		if link not in self.pixmaps:
			pic = QPixmap()
			data = DialogInsertPicture.dataFromPath(link, self.root)
			if data and pic.loadFromData(data[0]):
				self.pixmaps[link] = pic
		else:
			pic = self.pixmaps[link]
		self.now = pic

	def data(self):
		return self.now

	picture = Property(QPixmap, data)


class WebView(QWebView):
	""" ************************************************* web view ************************************************* """

	def __init__(self, root, parent=None):
		super().__init__(parent)
		# self.setContextMenuPolicy(Qt.NoContextMenu)
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)

		self.linkRenderer = WebLinkRenderer()
		self.imageRenderer = WebImageRenderer()
		self.mySettings = QSettings()
		self.setRoot(root)
		self.zoom = float(self.mySettings.value('View/Zoom', 1))
		if self.zoom < 0.3 or self.zoom > 5:
			self.zoom = 1
		self.setZoomFactor(self.zoom)

		self.init()

	def loadSettings(self):
		self.mySettings.beginGroup('View')
		font = loadFont(self.mySettings, makeFont('Helvetica', 12))
		QWebSettings.globalSettings().setFontFamily(QWebSettings.StandardFont, QFontInfo(font).family())
		QWebSettings.globalSettings().setFontSize(QWebSettings.DefaultFontSize, font.pointSize())
		self.mySettings.endGroup()

	def setRoot(self, root):
		self.imageRenderer.root = root

	def init(self):
		self.loadSettings()
		self.imageRenderer.clear()
		self.page().mainFrame().addToJavaScriptWindowObject('linkRenderer', self.linkRenderer)
		self.page().mainFrame().addToJavaScriptWindowObject('imageRenderer', self.imageRenderer)

	def setHtml(self, html):
		self.page().deleteLater()
		self.setPage(QWebPage())
		self.init()
		# super().setHtml(html, QUrl.fromLocalFile(QDir.currentPath() + '/')) # fucking '/' takes me 2 hrs
		super().setHtml(html, QUrl.fromLocalFile(APP_PATH))
		self.setZoomFactor(self.zoom)

	def wheelEvent(self, event):
		if event.modifiers() & Qt.ControlModifier:
			delta = float(event.delta() / 1200)
			self.zoom += delta

			if self.zoom < 0.3 or self.zoom > 5:
				self.zoom -= delta

			self.setZoomFactor(self.zoom)
			return
		super().wheelEvent(event)


def main():
	app = QApplication(sys.argv)

	QCoreApplication.setOrganizationName(AUTHOR)
	QCoreApplication.setApplicationName(APP_NAME)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()