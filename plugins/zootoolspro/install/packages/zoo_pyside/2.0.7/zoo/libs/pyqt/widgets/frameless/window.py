from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets.frameless.resizers import WindowResizer
from zoo.libs.pyqt.widgets.frameless.containerwidgets import DockingContainer, FramelessWindow
from zoo.libs.pyqt.widgets.frameless.widgets import FramelessOverlay, TitleBar, WindowContents
from zoo.core.util import env
from zoo.preferences import prefutils
from zoovendor.Qt import QtWidgets, QtCore
from zoo.libs.pyqt.widgets import layouts

MINIMIZED_WIDTH = 390


class KeyboardModifierFilter(QtCore.QObject):
    modifierPressed = QtCore.Signal()

    def eventFilter(self, obj, event):
        if FramelessOverlay is None:
            self.deleteLater()
            return


        if FramelessOverlay.isModifier():
            self.modifierPressed.emit()

        return super(KeyboardModifierFilter, self).eventFilter(obj, event)


class ZooWindow(QtWidgets.QWidget):
    closed = QtCore.Signal()

    def __init__(self, name="", title="", parent=None, resizable=True,
                 width=None, height=None, modal=False, alwaysShowAllTitle=False,
                 minButton=False, maxButton=False, onTop=False, saveWindowPref=True,
                 titleBar=None, overlay=True, minimizeEnabled=True, show=True):
        """ The frameless widget that will be subclassed by anything in zoo

        Will be attached to frameless widget or the docking container.

        """
        self.showOnInit = show
        super(ZooWindow, self).__init__(parent=None)
        self._minimized = False
        if titleBar is not None:  # todo: Maybe can do better?
            self.titleBar = titleBar(self, alwaysShowAll=alwaysShowAllTitle)
        else:
            self.titleBar = TitleBar(self, alwaysShowAll=alwaysShowAllTitle)

        self._saveWindowPref = saveWindowPref
        self._parentContainer = None  # type: FramelessWindow or DockingContainer
        self._minimizeEnabled = minimizeEnabled

        self.name = name
        self.title = title
        self._onTop = onTop
        self.setObjectName(name or title)
        self._modal = modal
        self._parent = parent
        self._initWidth = width
        self._initHeight = height
        self._alwaysShowAllTitle = alwaysShowAllTitle
        self._initUi()
        self.setTitle(title)
        self._connections()
        self.setResizable(resizable)
        self.overlay = None
        self.prevStyle = self.titleStyle()


        if overlay:
            self.overlay = FramelessOverlay(self, self.titleBar,
                                            topLeft=self.windowResizer.topLeftResize,
                                            topRight=self.windowResizer.topRightResize,
                                            botLeft=self.windowResizer.botLeftResize,
                                            botRight=self.windowResizer.botRightResize,
                                            resizable=resizable)
            self.overlay.widgetMousePress.connect(self.mousePressEvent)
            self.overlay.widgetMouseMove.connect(self.mouseMoveEvent)
            self.overlay.widgetMouseRelease.connect(self.mouseReleaseEvent)

        if not minButton:
            self.setMaxButtonVisible(False)

        if not maxButton:
            self.setMinButtonVisible(False)

        self.filter = KeyboardModifierFilter()
        self.filter.modifierPressed.connect(self.showOverlay)
        self.installEventFilter(self.filter)

    def setDefaultStyleSheet(self):
        """Try to set the default stylesheet, if not, just ignore it

        :return:
        """

        coreInterface = prefutils.coreInterface()
        result = coreInterface.stylesheet()
        self.setStyleSheet(result.data)

    def showOverlay(self):
        if self.overlay:
            self.overlay.show()

    def _initFramelessLayout(self):
        """ Initialise the frameless layout

        :return:
        :rtype:
        """
        self.setLayout(self._framelessLayout)

        self.mainContents = WindowContents(self)
        self.titleBar.setTitleText(self.title)

        self._framelessLayout.setHorizontalSpacing(0)
        self._framelessLayout.setVerticalSpacing(0)
        self._framelessLayout.setContentsMargins(0, 0, 0, 0)
        self._framelessLayout.addWidget(self.titleBar, 1, 1, 1, 1)
        self._framelessLayout.addWidget(self.mainContents, 2, 1, 1, 1)

        self._framelessLayout.setColumnStretch(1, 1)  # Title column
        self._framelessLayout.setRowStretch(2, 1)  # Main contents row

    @property
    def docked(self):
        """ Docked signal

        :return:
        :rtype: QtCore.Signal
        """

        return self.titleBar.logoButton.docked

    @property
    def undocked(self):
        """ Undocked signal

        :return:
        :rtype: QtCore.Signal
        """
        return self.titleBar.logoButton.undocked

    def setMainLayout(self, layout):
        """ Set the main layout

        :param layout:
        :type layout:
        :return:
        :rtype:
        """
        self.mainContents.setLayout(layout)

    def mainLayout(self):
        """ Main Layout

        Will generate a vBoxLayout if it is empty.

        :return:
        :rtype:
        """
        if self.mainContents.layout() is None:
            self.mainContents.setLayout(layouts.vBoxLayout())

        return self.mainContents.layout()

    def _connections(self):
        self.docked.connect(self.dockEvent)
        self.undocked.connect(self.undockedEvent)
        self.titleBar.doubleClicked.connect(self.titleDoubleClicked)

    def titleDoubleClicked(self):
        """ Title doubleclicked """
        if not self.isMinimized():
            self.minimize()
        else:
            self.maximize()

    def isMinimized(self):
        """ Window is minimized

        :return: 
        :rtype: bool
        """
        return self._minimized

    def setMinimizeEnabled(self, enabled):
        """

        :param enabled:
        :type
        :return:
        """
        self._minimizeEnabled = enabled

    def dockEvent(self, container):
        """ Dock event

        :return:
        :rtype:
        """
        if self.isMinimized():
            self.setUiMinimized(False)

        self.setMovable(False)
        self.hideResizers()
        self._parentContainer = container

    def undockedEvent(self):
        """ Undocked event

        :return:
        :rtype:
        """
        self.showResizers()
        self.setMovable(True)

    def maximize(self):
        """ Maximize UI """
        self.setUiMinimized(False)

        # Use the resized height
        self.window().resize(self.savedSize)

    def minimize(self):
        """ Minimize UI """
        if not self._minimizeEnabled:
            return

        self.savedSize = self.window().size()
        self.setUiMinimized(True)
        utils.processUIEvents()
        utils.singleShotTimer(lambda: self.window().resize(utils.dpiScale(MINIMIZED_WIDTH), 0))

    def setUiMinimized(self, minimize):
        """ Resizes the spacing, icons and hides only. 
        It doesn't resize the window.


        :param minimize:
        :type minimize: bool
        """
        self._minimized = minimize

        if minimize:
            if not self._minimizeEnabled:
                return

            self.prevStyle = self.titleStyle()
            self.setTitleStyle(TitleBar.TitleStyle.Thin)
            self.mainContents.hide()
            self.titleBar.leftContents.hide()
            self.titleBar.rightContents.hide()
        else:
            self.mainContents.show()
            self.setTitleStyle(self.prevStyle)
            self.titleBar.leftContents.show()
            self.titleBar.rightContents.show()

    def showResizers(self):
        """ Show resizers

        :return:
        :rtype:
        """
        self.windowResizer.show()

    def hide(self):
        """ Hide the window """
        self.parentContainer.hide()
        return super(ZooWindow, self).hide()

    def show(self):
        """ Show the window """
        self.parentContainer.show()
        return super(ZooWindow, self).show()

    def hideResizers(self):
        """ Hide resizers

        :return: 
        :rtype:
        """
        self.windowResizer.hide()

    def setTitleStyle(self, style):
        """ Set title style

        :param style: TitleStyle.Default or TitleStyle.Thin
        :type style: 
        """
        self.titleBar.setTitleStyle(style)


    def titleStyle(self):
        """ Get title style

        :return:
        """
        return self.titleBar.titleStyle()

    def setLogoColor(self, color):
        self.titleBar.logoButton.setIconColor(color)

    def setMaxButtonVisible(self, vis):
        self.titleBar.setMaxButtonVisible(vis)

    def setMinButtonVisible(self, vis):
        self.titleBar.setMinButtonVisible(vis)

    def _initUi(self):
        """ Initialize the UI

        :return:
        :rtype:
        """

        self.attachFramelessWindow(saveWindowPref=self._saveWindowPref)  # Initialized attached to the frameless

        self._minimized = False
        self._framelessLayout = QtWidgets.QGridLayout()
        self._initFramelessLayout()
        self.windowResizer = WindowResizer(parent=self, installToLayout=self._framelessLayout)
        if self.showOnInit:
            utils.singleShotTimer(self.showWindow)
        self.setDefaultStyleSheet()

    def centerToParent(self):
        """ Center widget to parent

        :return:
        """
        utils.updateWidgetSizes(self.parentContainer)
        size = self.rect().size()
        if self._parent:
            widgetCenter = utils.widgetCenter(self._parent)
            pos = self._parent.pos()
        else:
            widgetCenter = QtCore.QPoint(0,0) # todo: should be current monitor center
            pos = QtCore.QPoint(0, 0)

        self.parentContainer.move(widgetCenter +
                                  pos -
                                  QtCore.QPoint(size.width() / 2, size.height() / 3))

    def showWindow(self):
        # Show window
        self.centerToParent()
        self.parentContainer.show()

    def setName(self, name):
        """ Set the name of the widget

        :param name:
        :type name:
        :return:
        :rtype:
        """
        self.name = name

    def setTitle(self, text):
        """ Set the title text

        :param text:
        :type text:
        :return:
        :rtype:
        """
        self.titleBar.setTitleText(text)
        self.title = text

    @property
    def windowResizedFinished(self):
        return self.windowResizer.resizeFinished

    def setResizable(self, active):
        """ Window is resizable

        :param active:
        :type active:
        :return:
        :rtype:
        """
        self.windowResizer.setEnabled(active)

    def resizerHeight(self):
        """ Resizer height

        :return:
        :rtype:
        """
        return self.windowResizer.resizerHeight()

    def resizerWidth(self):
        """ Resizer Width

        :return:
        :rtype:
        """
        return self.windowResizer.resizerWidth()

    def attachFramelessWindow(self, show=False, saveWindowPref=True):
        """ Attach widget to frameless window

        :param show:
        :type show:
        :param disableSavePref: Restores positions from saved settings
        :type disableSavePref:
        :return:
        :rtype: FramelessWindow
        """
        self._parent = self._parent or parentWindow()

        self._parentContainer = FramelessWindow(self._parent,
                                                width=self._initWidth,
                                                height=self._initHeight,
                                                saveWindowPref=saveWindowPref,
                                                onTop=self._onTop)
        self._parentContainer.setWidget(self)
        if self._modal:
            self._parentContainer.setWindowModality(QtCore.Qt.ApplicationModal)

        self.centerToParent()
        if show:
            self.showWindow()

        return self._parentContainer

    def resizeWindow(self, width=-1, height=-1):
        """

        :param rect:
        :type rect: QtCore.QRect
        :return:
        """
        if width == -1:
            width = self.width()
        if height == -1:
            height = self.height()

        width += self.resizerWidth()*2
        height += self.resizerHeight()*2


        super(ZooWindow, self).resize(width, height)

    def keyPressEvent(self, event):
        if self.overlay and event.modifiers() == QtCore.Qt.AltModifier:
            self.overlay.show()

        return super(ZooWindow, self).keyPressEvent(event)

    @property
    def parentContainer(self):
        """

        :return:
        :rtype: :class:`FramelessWindow` or :class:`DockingContainer`
        """
        return self._parentContainer

    def isDocked(self):
        """

        :return:
        :rtype:
        """

        return self.parentContainer.isDockingContainer()

    def setMovable(self, movable):
        """ Movable through the titlebar

        :param movable:
        :type movable: bool
        :return:
        :rtype:
        """

        self.titleBar.setMoveEnabled(movable)

    def movable(self):
        return self.titleBar.moveEnabled()

    def close(self):
        """ Close window

        :return:
        :rtype:
        """
        super(ZooWindow, self).close()
        self.removeEventFilter(self.filter)

        self.closed.emit()

        if isinstance(self._parentContainer, FramelessWindow):
            self._parentContainer.close()
        elif isinstance(self._parentContainer, DockingContainer):
            self._parentContainer.close()


class ZooWindowThin(ZooWindow):
    """ Same as ZooWindow with modified title style

    """

    def _initFramelessLayout(self):
        super(ZooWindowThin, self)._initFramelessLayout()
        self.setTitleStyle(TitleBar.TitleStyle.Thin)
        self.titleBar.setTitleAlign(QtCore.Qt.AlignCenter)


def parentWindow():
    """

    :return:
    :rtype: QtWidgets.QWidget
    """
    if env.isInMaya():
        from zoo.libs.maya.qt import mayaui
        return mayaui.getMayaWindow()
    else:
        return None


def getZooWindows():
    """ Gets all frameless windows in the scene

    :return: All found window widgets under the Maya window
    """
    windows = []
    from zoo.libs.maya.qt import mayaui
    for child in mayaui.getMayaWindow().children():
        # if it has a zootoolsWindow property set, use that otherwise just use the child
        # w = child.property("zootoolsWindow") or child
        if isinstance(child, FramelessWindow):
            # windows.append(child.zooWindow)
            windows.append(child)

        #todo: add docked

    return windows
