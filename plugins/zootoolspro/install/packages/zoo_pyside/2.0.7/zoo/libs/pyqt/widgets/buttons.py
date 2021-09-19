from zoo.preferences import prefutils
from zoovendor.Qt import QtWidgets, QtCore
from zoo.libs.pyqt import uiconstants as uic, utils
from zoo.libs.pyqt.widgets import roundbutton, label, layouts, dpiscaling
from zoo.libs.pyqt.widgets.extendedbutton import ExtendedPushButton, ExtendedButton, ShadowedButton
from zoo.libs import iconlib
from zoo.preferences.core import preference

THEMEPREF = preference.interface("core_interface")


class OkCancelButtons(QtWidgets.QWidget):
    OkBtnPressed = QtCore.Signal()
    CancelBtnPressed = QtCore.Signal()

    def __init__(self, okText="OK", cancelTxt="Cancel", parent=None):
        """Creates OK Cancel Buttons bottom of window, can change the names

        :param okText: the text on the ok (first) button
        :type okText: str
        :param cancelTxt: the text on the cancel (second) button
        :type cancelTxt: str
        :param parent: the widget parent
        :type parent: class
        """
        super(OkCancelButtons, self).__init__(parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.okBtn = QtWidgets.QPushButton(okText, parent=self)
        self.cancelBtn = QtWidgets.QPushButton(cancelTxt, parent=self)
        self.layout.addWidget(self.okBtn)
        self.layout.addWidget(self.cancelBtn)
        self.connections()

    def connections(self):
        self.okBtn.clicked.connect(self.OkBtnPressed.emit)
        self.cancelBtn.clicked.connect(self.CancelBtnPressed.emit)


def buttonRound(**kwargs):
    """Create a rounded button usually just an icon only button with icon in a round circle

    This function is usually called via buttonStyled()
    Uses stylesheet colors, and icon color via the stylesheet from buttonStyled()

    :Note: WIP, Will fill out more options with time

    :param kwargs: See the doc string from the function buttonStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: object
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    toolTip = kwargs.get("toolTip", "")
    icon = kwargs.get("icon", (255, 255, 255))  # returns the name of the icon as a string only
    iconSize = kwargs.get("iconSize")
    iconColor = kwargs.get("iconColor")
    iconHoverColor = kwargs.get("iconHoverColor")  # TODO: add this functionality later
    btnWidth = kwargs.get("btnWidth", 24)
    btnHeight = kwargs.get("btnHeight", 24)

    iconObject = iconlib.iconColorized(icon, size=iconSize, color=iconColor)

    btn = roundbutton.RoundButton(parent=parent, text=text, icon=iconObject, toolTip=toolTip)
    btn.setFixedSize(QtCore.QSize(btnWidth, btnHeight))
    return btn


def styledButton(text=None, icon=None, parent=None, toolTip="", textCaps=False, iconColor=None, iconHoverColor=None,
                 minWidth=None, maxWidth=None, iconSize=16, overlayIconName=None, overlayIconColor=None, minHeight=None,
                 maxHeight=None, style=uic.BTN_DEFAULT, btnWidth=None, btnHeight=None, iconColorTheme=None,
                 themeUpdates=True):
    """ Create a button with text or an icon in various styles and options.

    Style - 0 - uic.BTN_DEFAULT - Default zoo extended button with optional text or an icon.
    Style - 1 - uic.BTN_TRANSPARENT_BG - Default zoo extended button w transparent bg.
    Style - 2 - uic.BTN_ICON_SHADOW - Main zoo IconPushButton button (icon in a colored box) with shadow underline
    Style - 3 - uic.BTN_DEFAULT_QT - Default style uses vanilla QPushButton and not zoo's extended button
    Style - 4 - uic.BTN_ROUNDED - # Rounded button stylesheeted bg color and stylesheeted icon color
    Style - 5 - uic.BTN_LABEL_SML - A regular Qt label with a small button beside

    :param text: The button text
    :type icon: str
    :param icon: The icon image name, icon is automatically sized.
    :type icon: str
    :param parent: The parent widget.
    :type parent: object
    :param toolTip: The tooltip as seen with mouse over extra information.
    :type toolTip: str
    :param style: The style of the button, 0 default, 1 no bg. See pyside.uiconstants BTN_DEFAULT, BTN_TRANSPARENT_BG.
    :type style: int
    :param textCaps: Bool to make the button text all caps.
    :type textCaps: bool
    :param iconColor: The color of the icon in 255 color eg (255, 134, 23)
    :type iconColor: tuple
    :param minWidth: minimum width of the button in pixels, DPI handled.
    :type minWidth: int
    :param maxWidth: maximum width of the button in pixels, DPI handled.
    :type maxWidth: int
    :param iconSize: The size of the icon in pixels, always square, DPI handled.
    :type iconSize: int
    :param overlayIconName: The name of the icon image that will be overlayed on top of the original icon.
    :param overlayIconName: tuple
    :param overlayIconColor: The color of the overlay image icon (255, 134, 23) :note: Not implemented yet.
    :type overlayIconColor: tuple
    :param minHeight: minimum height of the button in pixels, DPI handled.  Overrides min and max settings
    :type minHeight: int
    :param maxHeight: maximum height of the button in pixels, DPI handled.
    :type maxHeight: int
    :param btnWidth: the fixed width of the button is there is one, DPI handled.  Overrides min and max settings
    :type btnWidth: int
    :param btnHeight: the fixed height of the button is there is one, DPI handled.
    :type btnHeight: int
    :return qtBtn: returns a qt button widget.
    :rtype qtBtn: :class:`ShadowedButton` or :class:`QtWidgets.QPushButton` or :class:`roundbutton.RoundButton` or :class:`LabelSmlButton`
    """
    if btnWidth:
        minWidth = btnWidth
        maxWidth = btnWidth
    if btnHeight:
        minHeight = btnHeight
        maxHeight = btnHeight
    if not iconColor:
        iconColor = THEMEPREF.BUTTON_ICON_COLOR
    if not iconHoverColor:
        # todo: this is done automatically in extendedbuttons, this shouldn't be done here
        hoverOffset = 25
        iconHoverColor = iconColor
        iconHoverColor = tuple([min(255, c + hoverOffset) for c in iconHoverColor])
    if style == uic.BTN_DEFAULT or style == uic.BTN_TRANSPARENT_BG:

        return buttonExtended(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                              iconColor=iconColor, iconHoverColor=iconHoverColor, minWidth=minWidth,
                              maxWidth=maxWidth, iconSize=iconSize, overlayIconName=overlayIconName,
                              overlayIconColor=overlayIconColor, minHeight=minHeight, maxHeight=maxHeight,
                              style=style, iconColorTheme=iconColorTheme, themeUpdates=themeUpdates)
    elif style == uic.BTN_ICON_SHADOW:
        return iconShadowButton(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                                iconColor=iconColor, iconHoverColor=iconHoverColor, minWidth=minWidth,
                                maxWidth=maxWidth, iconSize=iconSize, overlayIconName=overlayIconName,
                                overlayIconColor=overlayIconColor, minHeight=minHeight, maxHeight=maxHeight)
    elif style == uic.BTN_DEFAULT_QT:
        return regularButton(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                             iconColor=iconColor, iconHoverColor=iconHoverColor, minWidth=minWidth, maxWidth=maxWidth,
                             iconSize=iconSize, overlayIconName=overlayIconName, overlayIconColor=overlayIconColor,
                             minHeight=minHeight, maxHeight=maxHeight)
    elif style == uic.BTN_ROUNDED:
        return buttonRound(text=text, icon=icon, parent=parent, toolTip=toolTip, iconColor=iconColor,
                           iconHoverColor=iconHoverColor, iconSize=iconSize, overlayIconName=overlayIconName,
                           overlayIconColor=overlayIconColor, btnWidth=btnWidth, btnHeight=btnHeight)
    elif style == uic.BTN_LABEL_SML:
        return LabelSmlButton(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                              iconColor=iconColor, iconHoverColor=iconHoverColor, minWidth=uic.BTN_W_ICN_MED,
                              maxWidth=uic.BTN_W_ICN_MED, iconSize=iconSize, overlayIconName=overlayIconName,
                              overlayIconColor=overlayIconColor, minHeight=minHeight, maxHeight=maxHeight)


def buttonExtended(**kwargs):
    """ Create an extended either transparent bg or regular style. Features all the extended button functionality

    Default Icon colour (None) is light grey and turns white (lighter in color) with mouse over.
    :Note: WIP, Will fill out more options with time

    :param kwargs: See the doc string from the function buttonStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: object
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    icon = kwargs.get("icon", "")  # returns the name of the icon as a string only
    toolTip = kwargs.get("toolTip", "")
    iconSize = kwargs.get("iconSize", 16)
    iconColor = kwargs.get("iconColor")
    iconHoverColor = kwargs.get("iconHoverColor")
    overlayIconName = kwargs.get("overlayIconName")
    overlayIconColor = kwargs.get("overlayIconColor")
    iconColorTheme = kwargs.get("iconColorTheme")
    minWidth = kwargs.get("minWidth")
    maxWidth = kwargs.get("maxWidth")
    minHeight = kwargs.get("maxHeight")
    maxHeight = kwargs.get("maxHeight")
    themeUpdates = kwargs.get("themeUpdates")
    style = kwargs.get("style")

    if icon:
        # todo: icon hover already gets done automatically use btn.setIconByName() instead
        if style == uic.BTN_DEFAULT:
            btn = ExtendedPushButton(parent=parent, text=text, iconColorTheme=iconColorTheme, themeUpdates=themeUpdates)
        else:
            btn = ExtendedButton(parent=parent, text=text, iconColorTheme=iconColorTheme, themeUpdates=themeUpdates)

        btn.setIconByName(icon, size=iconSize, colors=iconColor)  # todo add overlayIconName, overlayIconColor

    else:
        if style == uic.BTN_DEFAULT:
            btn = ExtendedPushButton(parent=parent, text=text, iconColorTheme=iconColorTheme)  # default style
        else:
            btn = ExtendedButton(parent=parent, text=text, iconColorTheme=iconColorTheme)  # transparent style
    btn.setToolTip(toolTip)

    if minWidth is not None:
        btn.setMinimumWidth(utils.dpiScale(minWidth))
    if maxWidth is not None:
        btn.setMaximumWidth(utils.dpiScale(maxWidth))
    if minHeight is not None:
        btn.setMinimumHeight(utils.dpiScale(minHeight))
    if maxHeight is not None:
        btn.setMaximumHeight(utils.dpiScale(maxHeight))
    return btn


def regularButton(**kwargs):
    """ Creates regular pyside button with text or an icon.

    :note: Will fill out more options with time.
    :note: Should probably override ExtendedButton and not QtWidgets.QPushButton for full options.

    :param kwargs: See the doc string from the function buttonStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: :class:`QtWidgets.QPushButton`
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    icon = kwargs.get("icon", THEMEPREF.BUTTON_ICON_COLOR)
    toolTip = kwargs.get("toolTip", "")
    iconSize = kwargs.get("iconSize", uic.BTN_W_ICN_REG)
    iconColor = kwargs.get("iconColor")
    overlayIconName = kwargs.get("overlayIconName")
    overlayIconColor = kwargs.get("overlayIconColor")
    minWidth = kwargs.get("minWidth")
    maxWidth = kwargs.get("maxWidth")
    minHeight = kwargs.get("maxHeight")
    maxHeight = kwargs.get("maxHeight")

    btn = QtWidgets.QPushButton(text, parent=parent)
    if icon:
        btn.setIcon(iconlib.iconColorized(icon, size=utils.dpiScale(iconSize), color=iconColor,
                                          overlayName=overlayIconName, overlayColor=overlayIconColor))

    btn.setToolTip(toolTip)
    if minWidth is not None:
        btn.setMinimumWidth(utils.dpiScale(minWidth))
    if maxWidth is not None:
        btn.setMaximumWidth(utils.dpiScale(maxWidth))
    if minHeight is not None:
        btn.setMinimumHeight(utils.dpiScale(minHeight))
    if maxHeight is not None:
        btn.setMaximumHeight(utils.dpiScale(maxHeight))
    return btn


def iconShadowButton(**kwargs):
    """ Create a button (ShadowedButton) with the icon in a coloured box and a button shadow at the bottom of the button.

    This function is usually called via buttonStyled()
    Uses stylesheet colors, and icon color via the stylesheet from buttonStyled()

    :Note: WIP, Will fill out more options with time

    :param kwargs: See the doc string from the function buttonStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: ShadowedButton
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    textCaps = kwargs.get("textCaps")
    icon = kwargs.get("icon", THEMEPREF.BUTTON_ICON_COLOR)  # returns the name of the icon as a string only
    toolTip = kwargs.get("toolTip", "")
    iconSize = kwargs.get("iconSize")
    iconColor = kwargs.get("iconColor")
    iconHoverColor = kwargs.get("iconHoverColor")  # TODO: add this functionality later
    minWidth = kwargs.get("minWidth")
    maxWidth = kwargs.get("maxWidth")
    minHeight = kwargs.get("minHeight")  # TODO: add this functionality later
    maxHeight = kwargs.get("maxHeight")
    btn = ShadowedButton(text=text, parent=parent, forceUpper=textCaps, toolTip=toolTip)
    btn.setIconByName(icon, colors=iconColor, size=iconSize)
    if maxHeight:
        btn.setFixedHeight(maxHeight)
    if maxWidth:
        btn.setMaximumWidth(maxWidth)
    if minWidth:
        btn.setMinimumWidth(minWidth)
    return btn


class LabelSmlButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, text="", icon=None, parent=None, toolTip="", textCaps=False, iconColor=None, iconHoverColor=None,
                 minWidth=None, maxWidth=None, iconSize=16, overlayIconName=None, overlayIconColor=None, minHeight=None,
                 maxHeight=None, style=uic.BTN_DEFAULT, btnWidth=None, btnHeight=None):
        """Creates a Qt label and a small button with icon, can be called as though it's a button with StyledButton()

        See StyledButton() for kwarg documentation
        """
        super(LabelSmlButton, self).__init__(parent=parent)
        self.text = text
        if text:
            self.label = label.Label(text, self, toolTip=toolTip, upper=textCaps)
        self.btn = buttonExtended(text="", icon=icon, parent=self, toolTip=toolTip, textCaps=textCaps,
                                  iconColor=iconColor, iconHoverColor=iconHoverColor, minWidth=minWidth,
                                  maxWidth=maxWidth, iconSize=iconSize, overlayIconName=overlayIconName,
                                  overlayIconColor=overlayIconColor, minHeight=minHeight, maxHeight=maxHeight,
                                  style=style)
        btnLayout = layouts.hBoxLayout(parent=self)
        if text:
            btnLayout.addWidget(self.label, 5)
        btnLayout.addWidget(self.btn, 1)
        self.connections()

    def _onClicked(self):
        """If the button is clicked emit"""
        self.clicked.emit()

    def setDisabled(self, state):
        """Disable the text (make it grey)"""
        self.btn.setDisabled(state)
        if self.text:
            self.label.setDisabled(state)

    def connections(self):
        self.btn.clicked.connect(self._onClicked)


class AlignedButton(ExtendedButton, dpiscaling.DPIScaling):
    def __init__(self, text="", parent=None, icon=None,
                 align=QtCore.Qt.AlignLeft, margins=(8, 0, 8, 0), spacing=3,
                 toolTip=None):
        self._kwargs = locals()
        self._icon = None
        self._label = None

        super(AlignedButton, self).__init__("", parent=parent)
        self._initUi()


    def _initUi(self):
        """ Initialize the ui

        :return:
        """
        self.setToolTip(self._kwargs['toolTip'])
        self._icon = AlignedButtonImage(self)
        self._label = QtWidgets.QLabel(self._kwargs['text'], parent=self)
        self.setLayout(layouts.hBoxLayout(margins=self._kwargs['margins'], spacing=self._kwargs['spacing']))

        self._iconSize = utils.sizeByDpi(QtCore.QSize(16, 16))

        self.mouseEntered = True
        self.iconPixmap = None  # type: QtGui.QPixmap
        self.iconHoveredPixmap = None  # type: QtGui.QPixmap
        self.iconPressedPixmap = None  # type: QtGui.QPixmap
        self.themePref = prefutils.coreInterface()
        self.setFixedHeight(24)

        if self._kwargs['align'] == QtCore.Qt.AlignRight:
            self.layout().addStretch(1)
        self.layout().addWidget(self._icon)
        self.layout().addWidget(self._label)
        if self._kwargs['align'] == QtCore.Qt.AlignLeft:
            self.layout().addStretch(1)
        self.setIconByName(self._kwargs['icon'], (192, 192, 192))


    def updateTheme(self, event):
        """ Update the theme

        :type event: preferences.interface.preference_interface.UpdateThemeEvent
        :return:
        :rtype:
        """
        if self._themeUpdatesColor:
            self.iconColorTheme = self.iconColorTheme or '$BUTTON_ICON_COLOR'
            iconColor = event.pref.stylesheetSettingColour(self.iconColorTheme, theme=event.theme)
            # self.imageWgt.setIconColor(iconColor)

    def setIcon(self, icon):
        """

        :param icon:
        :type  icon: zoovendor.Qt.QtGui.QIcon
        :return:
        """
        if not self._icon:
            return

        if icon:
            self._icon.setPixmap(icon.pixmap(self._icon.size()))
            self._icon.show()
        else:
            self._icon.hide()

    def setText(self, text):
        if self._label:
            self._label.setText(text)

    def setIconSize(self, size):
        """ Set the icon size

        :param size:
        :return:
        """
        self._iconSize = utils.sizeByDpi(size)
        self._icon.setFixedSize(self._iconSize)

    def mouseDoubleClickEvent(self, event):
        event.ignore()
        return super(AlignedButton, self).mouseDoubleClickEvent(event)

    def setFixedHeight(self, height):
        """ Set Fixed Height

        :param height: Height in pixels of the button
        :type height: int
        :return:
        """
        self.updateImageWidget(height)
        super(AlignedButton, self).setFixedHeight(height)

    def setFixedSize(self, size):
        """ Set the fixed size

        :param size: New fixed size of the widget
        :type size: QtCore.QSize

        :return:
        """
        self.updateImageWidget(size.height())
        super(AlignedButton, self).setFixedSize(size)

    def updateImageWidget(self, newHeight):
        """ Make sure the image widget is always square

        :param newHeight: The new height of the widget to update to
        :type newHeight: int
        :return:
        """

        self._icon.setFixedSize(utils.sizeByDpi(QtCore.QSize(newHeight, newHeight)))

    def setIconByName(self, iconNames, colors, size=None, hoverColor=None, pressedColor=None, iconScaling=None):
        """ Set Icon Size by name

        todo: needs additional features similar to the ButtonIcons.setIconByName() method

        :param size: Size of the icon in pixels
        :type size: int
        :param iconNames: Names of the icons
        :type iconNames: list or basestring
        :param colors: Colors of the icons
        :type colors: list of tuple or tuple
        :return:
        """
        self._icon.show()
        if size is not None:
            self.setIconSize(QtCore.QSize(size, size))

        hoverColor = hoverColor or colors
        pressedColor = pressedColor or colors

        colors = [colors]
        hoverColor = [hoverColor]
        pressedColor = [pressedColor]
        self.iconNames = iconNames

        # if self.isMenu and isinstance(iconNames, string_types):
        #     self.iconNames = [iconNames, self._menuIndicatorIcon]
        #     colors += colors
        #     hoverColor += hoverColor
        #     pressedColor += pressedColor

        newSize = self._iconSize.width()
        self.iconPixmap = iconlib.iconColorizedLayered(self.iconNames, colors=colors, size=newSize,
                                                       iconScaling=iconScaling). \
            pixmap(QtCore.QSize(newSize, newSize))

        self.iconHoveredPixmap = iconlib.iconColorizedLayered(self.iconNames, colors=hoverColor, size=newSize,
                                                              iconScaling=iconScaling). \
            pixmap(QtCore.QSize(newSize, newSize))

        self.iconPressedPixmap = iconlib.iconColorizedLayered(self.iconNames, colors=pressedColor, size=newSize,
                                                              iconScaling=iconScaling). \
            pixmap(QtCore.QSize(newSize, newSize))

        self._icon.setPixmap(self.iconPixmap)

    def enterEvent(self, event):
        self.mouseEntered = True
        utils.setStylesheetObjectName(self, "")
        utils.setStylesheetObjectName(self._label, "shadowedLabelHover")
        self._icon.setPixmap(self.iconHoveredPixmap)

    def leaveEvent(self, event):
        self.mouseEntered = False
        utils.setStylesheetObjectName(self, "")
        utils.setStylesheetObjectName(self._label, "")
        self._icon.setPixmap(self.iconPixmap)

    def mousePressEvent(self, event):
        utils.setStylesheetObjectName(self._label, "shadowedLabelPressed")
        utils.setStylesheetObjectName(self, "shadowedButtonPressed")
        self._icon.setPixmap(self.iconPressedPixmap)
        return super(AlignedButton, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # If mouse still entered while mouse released then set it back to hovered style
        if self.mouseEntered:
            self.enterEvent(event)

        return super(AlignedButton, self).mouseReleaseEvent(event)


class AlignedButtonImage(QtWidgets.QLabel, dpiscaling.DPIScaling):
    """ CSS Purposes """