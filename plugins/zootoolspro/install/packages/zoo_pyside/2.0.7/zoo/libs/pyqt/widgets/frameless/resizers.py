from zoovendor.Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt import utils
from zoo.libs.utils import zlogging
logger = zlogging.getLogger(__name__)


class ResizeDirection:
    """ Flag attributes to tell the what position the resizer is """
    Left = 1
    Top = 2
    Right = 4
    Bottom = 8


class Resizers:
    Vertical = 1
    Horizontal = 2
    Corners = 4
    All = Vertical | Horizontal | Corners


class WindowResizer(QtCore.QObject):

    resizeFinished = QtCore.Signal()

    def __init__(self, parent, installToLayout=None, debug=False):
        """ Window Resizer

        :param parent:
        :type parent:
        :param installToLayout:
        :type installToLayout:
        """

        self.framelessParent = parent
        self.layout = None
        self._debug = debug
        super(WindowResizer, self).__init__(parent=parent)

        self.installToLayout(installToLayout)
        self.connections()

    def installToLayout(self, layout):
        """

        :param layout:
        :type layout: Qt.QtWidgets.QGridLayout
        :return:
        :rtype:
        """
        if not isinstance(layout, QtWidgets.QGridLayout):
            logger.error("WindowResizer expects a QtWidgets.QGridLayout")
            return

        self.layout = layout

        self.topResize = VerticalResize()
        self.botResize = VerticalResize()
        self.rightResize = HorizontalResize()
        self.leftResize = HorizontalResize()
        self.topLeftResize = CornerResize()
        self.topRightResize = CornerResize()
        self.botLeftResize = CornerResize()
        self.botRightResize = CornerResize()

        self.resizers = [self.topResize, self.topRightResize, self.rightResize,
                         self.botRightResize, self.botResize, self.botLeftResize,
                         self.leftResize, self.topLeftResize]

        for r in self.resizers:
            r.setParent(self.framelessParent)

        self.horizontalResizers = (self.leftResize, self.rightResize)
        self.verticalResizers = (self.topResize, self.botResize)
        self.cornerResizers = (self.topLeftResize, self.topRightResize, self.botLeftResize, self.botRightResize)

        layout.addWidget(self.topLeftResize, 0, 0, 1, 1)
        layout.addWidget(self.topResize, 0, 1, 1, 1)
        layout.addWidget(self.topRightResize, 0, 2, 1, 1)

        layout.addWidget(self.leftResize, 1, 0, 2, 1)
        layout.addWidget(self.rightResize, 1, 2, 2, 1)

        layout.addWidget(self.botLeftResize, 3, 0, 1, 1)
        layout.addWidget(self.botResize, 3, 1, 1, 1)
        layout.addWidget(self.botRightResize, 3, 2, 1, 1)

        self.setResizeDirections()

    def hide(self):
        """ Hide the resizers

        :return:
        :rtype:
        """
        for r in self.resizers:
            r.hide()

    def show(self):
        """ Show the resizers

        :return:
        :rtype:
        """
        for r in self.resizers:
            r.show()

    def connections(self):
        """ Connections

        :return:
        :rtype:
        """
        for r in self.resizers:
            r.windowResizedFinished.connect(self.resizeFinished.emit)

    def setResizeDirections(self):
        """Set the resize directions for the resize widgets for the window
        """
        # Horizontal/Vertical Resizers
        self.topResize.setResizeDirection(ResizeDirection.Top)
        self.botResize.setResizeDirection(ResizeDirection.Bottom)
        self.rightResize.setResizeDirection(ResizeDirection.Right)
        self.leftResize.setResizeDirection(ResizeDirection.Left)

        # Corner Resizers
        self.topLeftResize.setResizeDirection(ResizeDirection.Left | ResizeDirection.Top)
        self.topRightResize.setResizeDirection(ResizeDirection.Right | ResizeDirection.Top)
        self.botLeftResize.setResizeDirection(ResizeDirection.Left | ResizeDirection.Bottom)
        self.botRightResize.setResizeDirection(ResizeDirection.Right | ResizeDirection.Bottom)

    def resizerWidth(self):
        """ Calculates the total width of the vertical resizers
        """
        resizers = [self.leftResize, self.rightResize]
        ret = 0
        for r in resizers:
            if not r.isHidden():
                ret += r.minimumSize().width()

        return ret

    def setResizerActive(self, active):
        """Enable or disable the resizers

        :param active:
        """

        if active:
            self.show()
        else:
            self.hide()

    def resizerHeight(self):
        """Calculates the total height of the vertical resizers
        """
        resizers = [self.topResize, self.botResize]
        ret = 0
        for r in resizers:
            if not r.isHidden():
                ret += r.minimumSize().height()

        return ret

    def setEnabled(self, enabled):
        """ Set resizers enabled

        :param enabled:
        :type enabled:
        :return:
        :rtype:
        """
        [r.setEnabled(enabled) for r in self.resizers]


class ResizeBase(QtWidgets.QFrame):
    """
    The resize widgets for the sides of the windows and the corners to resize the parent window.

    """
    windowResized = QtCore.Signal()
    windowResizeStartEvent = QtCore.Signal()
    windowResizedFinished = QtCore.Signal()

    def __init__(self, parent, debug=False):
        super(ResizeBase, self).__init__(parent=parent)
        self.initUi()
        self.direction = 0  # ResizeDirection
        self.widgetMousePos = None  # QtCore.QPoint
        self.widgetGeometry = None  # type: QtCore.QRect

        if not debug:
            self.setStyleSheet("background-color:transparent;")
        else:
            self.setStyleSheet("background-color: #88990000;")
        self.frameless = None

        self.windowResizeStartEvent.connect(self.windowResizeStart)

    def initUi(self):
        self.windowResized.connect(self.windowResizeEvent)

    def paintEvent(self, event):
        """ Mouse events seem to deactivate when its completely transparent. Hacky way to avoid that for now.

        :type event: :class:`QtCore.QEvent`
        """

        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(255, 0, 0, 0))
        painter.end()

    def leaveEvent(self, event):
        """ Turn the mouse back to original

        :type event: :class:`QtCore.QEvent`
        """

        utils.restoreCursor()
        return event


    def windowResizeStart(self):
        self.widgetMousePos = self.mapFromGlobal(QtGui.QCursor.pos())
        self.widgetGeometry = self.window().frameGeometry()

    def mousePressEvent(self, event):
        self.windowResizeStartEvent.emit()

    def mouseMoveEvent(self, event):
        self.windowResized.emit()

    def setParent(self, parent):
        """Set the parent and the window

        :param parent:
        """
        self.frameless = parent
        super(ResizeBase, self).setParent(parent)

    def windowResizeEvent(self):
        """ Resize based on the mouse position and the current direction
        """
        pos = QtGui.QCursor.pos()
        newGeometry = self.window().frameGeometry()

        # Minimum Size
        mW = self.window().minimumSize().width()
        mH = self.window().minimumSize().height()

        # Check to see if the ResizeDirection flag is in self.direction
        if self.direction & ResizeDirection.Left == ResizeDirection.Left:
            left = newGeometry.left()
            newGeometry.setLeft(pos.x() - self.widgetMousePos.x())
            if newGeometry.width() <= mW:  # Revert back if too small
                newGeometry.setLeft(left)
        if self.direction & ResizeDirection.Top == ResizeDirection.Top:
            top = newGeometry.top()
            newGeometry.setTop(pos.y() - self.widgetMousePos.y())
            if newGeometry.height() <= mH:  # Revert back if too small
                newGeometry.setTop(top)
        if self.direction & ResizeDirection.Right == ResizeDirection.Right:
            newGeometry.setRight(pos.x() + (self.minimumSize().width() - self.widgetMousePos.x()))
        if self.direction & ResizeDirection.Bottom == ResizeDirection.Bottom:
            newGeometry.setBottom(pos.y() + (self.minimumSize().height() - self.widgetMousePos.y()))

        # Set new sizes
        x = newGeometry.x()
        y = newGeometry.y()
        w = max(newGeometry.width(), mW)  # Minimum Width
        h = max(newGeometry.height(), mH)  # Minimum height

        self.window().setGeometry(x, y, w, h)

    def setResizeDirection(self, direction):
        """Set the resize direction. Expects an int from ResizeDirection

        .. code-block:: python

            setResizeDirection(ResizeDirection.Left | ResizeDirection.Top)

        :param direction: ResizeDirection
        :type direction: int
        """
        self.direction = direction

    def mouseReleaseEvent(self, event):
        self.windowResizedFinished.emit()


class CornerResize(ResizeBase):
    """ Resizers in the corner of the window

    """

    def __init__(self, parent=None):
        super(CornerResize, self).__init__(parent=parent)

    def initUi(self):
        super(CornerResize, self).initUi()

        self.setFixedSize(utils.sizeByDpi(QtCore.QSize(10, 10)))

    def enterEvent(self, event):
        """ Set cursor based on corner hovered

        :type event: :class:`QtCore.QEvent`
        """

        if not self.isEnabled():
            return

        # Top Left or Bottom Right
        if self.direction == ResizeDirection.Left | ResizeDirection.Top or \
                self.direction == ResizeDirection.Right | ResizeDirection.Bottom:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeFDiagCursor)

            # Top Right or Bottom Left
        elif self.direction == ResizeDirection.Right | ResizeDirection.Top or \
                self.direction == ResizeDirection.Left | ResizeDirection.Bottom:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeBDiagCursor)


class VerticalResize(ResizeBase):
    """ Resizers for the top and bottom of the window

    """

    def __init__(self, parent=None):
        super(VerticalResize, self).__init__(parent=parent)

    def initUi(self):
        super(VerticalResize, self).initUi()
        self.setFixedHeight(utils.dpiScale(8))

    def enterEvent(self, event):
        """Change cursor on hover

        :type event: :class:`QtCore.QEvent`
        """
        if not self.isEnabled():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeVerCursor)


class HorizontalResize(ResizeBase):
    """ Resizers for the left and right of the window

    """

    def __init__(self, parent=None):
        super(HorizontalResize, self).__init__(parent=parent)

    def initUi(self):
        super(HorizontalResize, self).initUi()
        self.setFixedWidth(utils.dpiScale(8))

    def enterEvent(self, event):
        """Change cursor on hover

        :type event: :class:`QtCore.QEvent`
        """
        if not self.isEnabled():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)
