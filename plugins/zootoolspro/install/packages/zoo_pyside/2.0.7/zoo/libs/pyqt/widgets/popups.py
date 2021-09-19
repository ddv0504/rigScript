import uuid

from zoo.libs import iconlib
from zoo.libs.utils import strutils
from zoovendor.Qt import QtWidgets, QtCore
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets import layouts, buttons
from zoo.libs.pyqt.widgets.frameless import window


def FileDialog_directory(windowName="", parent="", defaultPath=""):
    """simple function for QFileDialog.getExistingDirectory, a window popup that searches for a directory

    Browses for a directory with a fileDialog window and returns the selected directory

    :param windowName: The name of the fileDialog window
    :type windowName: str
    :param parent: The parent widget
    :type parent: Qt.widget
    :param defaultPath: The default directory path, where to open the fileDialog window
    :type defaultPath: str
    :return directoryPath: The selected full directory path
    :rtype directoryPath: str
    """
    directoryPath = str(QtWidgets.QFileDialog.getExistingDirectory(parent, windowName, defaultPath))
    if not directoryPath:
        return
    return directoryPath


def generateName(name):
    """ Generate name

    :param name:
    :return:
    """
    return "{}_{}_".format(name, str(uuid.uuid4())[:4])


class MessageBox(window.ZooWindowThin):
    Warning = QtWidgets.QMessageBox.Warning
    Question = QtWidgets.QMessageBox.Question
    Info = QtWidgets.QMessageBox.Information
    Critical = QtWidgets.QMessageBox.Critical
    NoIcon = QtWidgets.QMessageBox.NoIcon
    _questionIcon = "help"
    _criticalIcon = "xCircleMark2"
    _warningIcon = "warning"
    _infoIcon = "information"

    def __init__(self, parent, title="", message="", icon="Question",
                 buttonA="OK", buttonB=None, buttonC=None, default=0, onTop=True):
        """ Message box

        :param parent:
        :type parent:
        :param title:
        :type title:
        :param message:
        :type message:
        :param buttonA:
        :type buttonA:
        :param buttonB:
        :type buttonB:
        :param buttonC:
        :type buttonC:
        :param icon:
        :type icon:
        """
        self._initArgs = locals()
        self.default = default

        super(MessageBox, self).__init__(parent=parent, title=title, name=generateName(icon), resizable=False, width=100,
                                         height=100, modal=False, minimizeEnabled=False, onTop=onTop)
        self.result = None
        self.msgClosed = False
        self.buttons = []  # type: list[QtWidgets.QPushButton]

        self._initMessageBox()


    def _initMessageBox(self):
        """ Init message box

        :return:
        """
        self.setMaxButtonVisible(False)
        self.setMinButtonVisible(False)
        self.titleBar.setTitleAlign(QtCore.Qt.AlignCenter)

        # Label
        label = QtWidgets.QLabel(self._initArgs['message'])
        width = min(label.fontMetrics().boundingRect(label.text()).width() + 20, 400)
        label.setFixedWidth(width)
        label.setWordWrap(True)
        height = min(self.calcLabelHeight(label=label, text=label.text()), 800)
        label.setFixedHeight(height)

        layoutText = layouts.hBoxLayout(margins=(15, 15, 15, 15), spacing=15)
        # MessageBox Image
        image = QtWidgets.QToolButton(parent=self)
        s = 32
        icon = self._initArgs['icon']
        if icon == "Warning":
            image.setIcon(iconlib.iconColorizedLayered(self._warningIcon, s, colors=(220, 210, 0)))
        elif icon == "Question":
            image.setIcon(iconlib.iconColorizedLayered(self._questionIcon, s, colors=(0, 192, 32)))
        elif icon == "Information":
            image.setIcon(iconlib.iconColorizedLayered(self._infoIcon, s, colors=(220, 220, 220)))
        elif icon == "Critical":
            image.setIcon(iconlib.iconColorizedLayered(self._criticalIcon, s, colors=(200, 90, 90)))
        elif icon == "NoIcon":
            pass

        if icon != "NoIcon":
            image.setIconSize(QtCore.QSize(s, s))
            image.setFixedSize(QtCore.QSize(s, s))

        label.setAlignment(QtCore.Qt.AlignTop)

        layoutText.addWidget(image)
        layoutText.addWidget(label)

        # Buttons
        layoutButtons = layouts.hBoxLayout(margins=(10, 0, 10, 10))
        layoutButtons.addStretch(1)

        msgButtons = [self._initArgs['buttonA'], self._initArgs['buttonB'], self._initArgs['buttonC']]
        res = ['A', 'B', 'C']


        for i, b in enumerate(msgButtons):
            if b is not None:
                button = buttons.styledButton(parent=self.parentWidget(), text=b)

                self.buttons.append(button)
                button.setMinimumWidth(80)
                button.setMinimumHeight(24)
                utils.setHSizePolicy(button, QtWidgets.QSizePolicy.MinimumExpanding)                

                layoutButtons.addWidget(button)
                button.leftClicked.connect(lambda res=res[i]: self.close(res))

        layoutButtons.addStretch(1)

        self.mainLayout().addLayout(layoutText)
        self.mainLayout().addLayout(layoutButtons)

    def keyPressEvent(self, event):
        """ keyPress event

        :param event:
        :return:
        """
        if self.default > 0:
            keys = [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Space]
            if any(map(lambda y: event.key() == y, keys)):
                self.buttons[self.default].clicked.emit()

    @classmethod
    def calcLabelHeight(cls, text, label):
        """

        :param text:
        :type text:
        :param label:
        :type label: QtWidgets.QLabel
        :return:
        :rtype:
        """
        # If this is too slow should map out text
        fm = label.fontMetrics()
        width = label.size().width()
        height = fm.height()
        lines = 1
        walkWidth = 0



        for c in text:
            w = cls.horizontalAdvance(fm, c)
            walkWidth += w + 1.1  # not sure where the 1.1 comes from, will have to find out
            if walkWidth > width:
                walkWidth = w
                lines += 1

        newLines = strutils.newLines(text)
        lines += newLines

        return height * lines

    @classmethod
    def horizontalAdvance(cls, fm, c):
        """ Horizontal advance doesn't exist in 2018. eg older versions of PySide2

        :param fm:
        :param c:
        :return:
        """

        if hasattr(fm, "horizontalAdvance"):
            return fm.horizontalAdvance(c)
        else:
            return fm.width(c)

    def close(self, result=None):
        self.msgClosed = True
        self.result = result
        super(MessageBox, self).close()

    @classmethod
    def showQuestion(cls, parent=None, title="", message="", buttonA="Continue", buttonB="Cancel", buttonC=None,
                     icon="Question", default=-1):
        m = MessageBox(parent=parent, title=title, message=message,
                       buttonA=buttonA, buttonB=buttonB, buttonC=buttonC,
                       icon=icon, default=default)

        while m.msgClosed is False:
            utils.processUIEvents()

        return m.result

    @classmethod
    def showWarning(cls, parent=None, title="", message="", buttonA="OK", buttonB="Cancel", buttonC=None,
                    icon="Warning", default=-1):
        m = MessageBox(parent=parent, title=title, message=message,
                       buttonA=buttonA, buttonB=buttonB, buttonC=buttonC,
                       icon=icon, default=default)

        while m.msgClosed is False:
            utils.processUIEvents()

        return m.result

    @classmethod
    def showCritical(cls, parent=None, title="", message="", buttonA="OK", buttonB="Cancel", buttonC=None,
                    icon="Critical", default=-1):
        m = MessageBox(parent=parent, title=title, message=message,
                       buttonA=buttonA, buttonB=buttonB, buttonC=buttonC,
                       icon=icon, default=default)

        while m.msgClosed is False:
            utils.processUIEvents()

        return m.result


    @classmethod
    def showOK(cls, title="Confirm", parent=None, message="Proceed", icon="Question",
               default=-1):
        """Simple function for ok/cancel QMessageBox.question, a window popup that with ok/cancel buttons

        :param title: The name of the ok/cancel window
        :type title: str
        :param parent: The parent widget
        :type parent: Qt.widget
        :param message: The message to ask the user
        :type message: str
        :return okPressed: True if the Ok button was pressed, False if cancelled
        :rtype okPressed: bool
        """
        m = MessageBox(parent=parent, title=title, message=message,
                       buttonA="OK", buttonB="Cancel", icon=icon, default=default)

        while m.msgClosed is False:
            utils.processUIEvents()

        return m.result == "A"

    @classmethod
    def showSave(cls, title="Confirm", parent=None, message="Proceed?",
                 showDiscard=True, default=-1):
        """Simple function for save/don't save/cancel QMessageBox.question, a window popup with buttons

        Can have two or three buttons:

            showDiscard True: Save, Discard, Cancel
            showDiscard False: Save, Cancel

        :param title: The name of the ok/cancel window
        :type title: str
        :param parent: The parent widget
        :type parent: Qt.widget
        :param message: The message to ask the user
        :type message: str
        :return buttonClicked: "cancel", "save", or "discard"
        :rtype buttonClicked: str
        """
        discard = None
        if showDiscard:
            discard = "Discard"

        m = MessageBox(parent=parent, title=title, message=message,
                       buttonA="Save", buttonB=discard, buttonC="Cancel", icon="Question", default=default)

        while m.msgClosed is False:
            utils.processUIEvents()

        if m.result == "A":
            return "save"
        elif m.result == "B":
            return "discard"

        return "cancel"


class MessageBoxQt(object):
    @classmethod
    def showQuestion(cls, parent, windowName, message, buttonA="Continue", buttonB="Cancel", buttonC=None,
                     icon="Question"):
        """Simple function for a dialog window with two or three buttons with changeable button names.

        buttonC=None will not show the third button.

        Icons are "NoIcon", "Warning", "Question", "Information" or "Critical"

        Returns strings "A", "B" or "C" depending on the button pressed.

        :param parent: The parent widget, can leave as None and will parent to Maya
        :type parent: object
        :param windowName: The name title of the window
        :type windowName: str
        :param message: The message/question as presented to the user inside the window
        :type message: str
        :param buttonA: The string name of the first button
        :type buttonA: str
        :param buttonB: The string name of the second button
        :type buttonB: str
        :param buttonC: The string name of the third (optional) button, if None is ignored
        :type buttonC: str

        :return buttonPressed: The button pressed, either "A", "B" or "C"
        :rtype buttonPressed: str
        """
        box = QtWidgets.QMessageBox(parent=parent)
        if icon == "Warning":
            box.setIcon(QtWidgets.QMessageBox.Warning)
        elif icon == "Question":
            box.setIcon(QtWidgets.QMessageBox.Question)
        elif icon == "Information":
            box.setIcon(QtWidgets.QMessageBox.Information)
        elif icon == "Critical":
            box.setIcon(QtWidgets.QMessageBox.Critical)
        elif icon == "NoIcon":
            box.setIcon(QtWidgets.QMessageBox.NoIcon)
        box.setWindowTitle(windowName)
        box.setText(message)
        buttonA_pressed = box.addButton(buttonA, QtWidgets.QMessageBox.YesRole)
        buttonB_pressed = box.addButton(buttonB, QtWidgets.QMessageBox.NoRole)
        if buttonC:
            buttonC_pressed = box.addButton(buttonC, QtWidgets.QMessageBox.NoRole)
        else:
            buttonC_pressed = None
        box.exec_()
        if box.clickedButton() == buttonA_pressed:
            return "A"
        elif box.clickedButton() == buttonB_pressed:
            return "B"
        elif box.clickedButton() == buttonC_pressed:
            return "C"
        else:
            return None

    @classmethod
    def showOK(cls, windowName="Confirm", parent=None, message="Proceed?", okButton=QtWidgets.QMessageBox.Ok):
        """Simple function for ok/cancel QMessageBox.question, a window popup that with ok/cancel buttons

        :param windowName: The name of the ok/cancel window
        :type windowName: str
        :param parent: The parent widget
        :type parent: Qt.widget
        :param message: The message to ask the user
        :type message: str
        :return okPressed: True if the Ok button was pressed, False if cancelled
        :rtype okPressed: bool
        """
        result = QtWidgets.QMessageBox.question(parent, windowName, message, QtWidgets.QMessageBox.Cancel | okButton)
        if result != QtWidgets.QMessageBox.Cancel:
            return True
        return False

    @classmethod
    def showSave(cls, windowName="Confirm", parent=None, message="Proceed?", showDiscard=True):
        """Simple function for save/don't save/cancel QMessageBox.question, a window popup with buttons

        Can have two or three buttons:

            showDiscard True: Save, Discard, Cancel
            showDiscard False: Save, Cancel

        :param windowName: The name of the ok/cancel window
        :type windowName: str
        :param parent: The parent widget
        :type parent: Qt.widget
        :param message: The message to ask the user
        :type message: str
        :return buttonClicked: "cancel", "save", or "discard"
        :rtype buttonClicked: str
        """
        if showDiscard:
            result = QtWidgets.QMessageBox.question(parent, windowName, message,
                                                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard
                                                    | QtWidgets.QMessageBox.Cancel)

        else:
            result = QtWidgets.QMessageBox.question(parent, windowName, message,
                                                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)

        if result == QtWidgets.QMessageBox.Cancel:
            return "cancel"
        if result == QtWidgets.QMessageBox.Save:
            return "save"
        if result == QtWidgets.QMessageBox.Discard:
            return "discard"


def InputDialog(windowName="Add Name", textValue="", parent=None, message="Rename?", windowWidth=270, windowHeight=100):
    """Opens a simple QT window that locks the program asking the user to input a string into a text box

    Useful for renaming etc.

    :param windowName: The name of the ok/cancel window
    :type windowName: str
    :param textValue: The initial text in the textbox, eg. The name to be renamed
    :type textValue: str
    :param parent: The parent widget
    :type parent: Qt.widget
    :param message: The message to ask the user
    :type message: str
    :return newTextValue: The new text name entered
    :rtype newTextValue: str
    """
    dialog = QtWidgets.QInputDialog(parent)
    dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
    dialog.setTextValue(textValue)
    dialog.setWindowTitle(windowName)
    dialog.setLabelText(message)
    dialog.resize(utils.dpiScale(windowWidth), utils.dpiScale(windowHeight))
    ok = dialog.exec_()
    newTextValue = dialog.textValue()
    if not ok:
        return ""
    return newTextValue


def SaveDialog(directory, fileExtension="", nameFilters=""):
    """Opens a Qt save window with options for saving a file.

    Returns the path of the file to be created, or "" if the cancel button was clicked.

    Also see MessageBox.showSave() which has the option for saving the current scene. With save, cancel or discard.

    :param directory: The path of the directory to default when the dialog window appears
    :type directory: str
    :param fileExtension: Optional fileExtension eg ".zooScene"
    :type fileExtension:
    :param nameFilters: Optional list of filters, example ['ZOOSCENE (*.zooScene)']
    :type nameFilters: list(str)
    :return fullFilePath: The fullPath of the file to be saved, else "" if cancelled
    :rtype fullFilePath: str
    """
    saveDialog = QtWidgets.QFileDialog()
    if fileExtension:
        saveDialog.setDefaultSuffix(fileExtension)
    saveDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    saveDialog.setDirectory(directory)
    if nameFilters:
        saveDialog.setNameFilters(nameFilters)
    if saveDialog.exec_() == QtWidgets.QDialog.Accepted:
        return saveDialog.selectedFiles()[0]
    else:
        return ""
