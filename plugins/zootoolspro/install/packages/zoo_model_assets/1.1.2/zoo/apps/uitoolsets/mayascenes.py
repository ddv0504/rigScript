import os
import webbrowser



from zoovendor.Qt import QtWidgets

from zoo.core.util import env
from zoo.libs.utils import filesystem, output
from zoo.apps.model_assets import assetconstants as ac
from zoo.apps.model_assets import assetdirectories
from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.apps.toolsetsui.widgets.toolsetresizer import ToolsetResizer

from zoo.apps.toolsetsui import toolsetui
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs.utils import zlogging
from zoo.preferences import preferencesconstants as pc
from zoo.preferences.core import preference

if env.isInMaya():
    from maya import cmds
    from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.libs.pyqt.extended.imageview.models import mayafilemodel


logger = zlogging.getLogger(__name__)

DFLT_RNDR_LIST = ["Arnold", "Redshift", "Renderman", "VRay"]  # only used for filtering
DFLT_RNDR_MODES = [("arnold", "Arnold"), ("redshift", "Redshift"), ("renderman", "Renderman")]
UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

mayaScenesIcon = "logOut"


class MayaScenes(toolsetwidget.ToolsetWidget):
    id = "mayaScenes"
    uiData = {"label": "Maya Scenes",
              "icon": mayaScenesIcon,
              "tooltip": "Mini browser for Maya Scenes",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-maya-scenes/"
              }

    # ------------------------------------
    # START UP
    # ------------------------------------

    def preContentSetup(self):
        """First code to run"""
        self.toolsetWidget = self  # needed for callback decorators
        self.mayaScenesPrefsData = preference.findSetting(ac.RELATIVE_MAYA_PREFS_FILE, None)  # maya asset .prefs info
        self.generalSettingsPrefsData = preference.findSetting(pc.RELATIVE_PREFS_FILE, None)  # renderer in general pref
        self.properties.rendererIconMenu.value = self.generalSettingsPrefsData[pc.PREFS_KEY_RENDERER]
        self.setPrefVariables()  # sets self.directory and self.uniformIcons
        if not self.directory:  # directory can be empty if preferences window hasn't been opened
            # so update the preferences json file with default locations
            self.mayaScenesPrefsData = assetdirectories.buildUpdateMayaScenesPrefs(self.mayaScenesPrefsData)
            self.setPrefVariables()

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self,
                                        directory=self.directory, uniformIcons=self.uniformIcons)
        return self.compactWidget

    def postContentSetup(self):
        """Last of the initizialize code"""
        self.setRenderer(updateAllUIs=False)  # Updates the renderer filtering on startup.
        self.uiconnections()  # Connects buttons and other widgets

    def currentWidget(self):
        """ Current active widget

        :return:
        :rtype:  AllWidgets
        """
        return super(MayaScenes, self).currentWidget()

    def widgets(self):
        """ List of widgets

        :return:
        :rtype: list[AllWidgets]
        """
        return super(MayaScenes, self).widgets()

    # ------------------------------------
    # PROPERTIES
    # ------------------------------------

    def initializeProperties(self):
        return [{"name": "rendererIconMenu", "label": "", "value": "Arnold"}]

    def updateFromProperties(self):
        """ Runs update properties from the base class.

        Widgets will auto update from self.properties if linked via:

            self.linkProperty(widget, "propertyKey")
            or
            self.toolsetWidget.linkProperty(widget, "propertyKey")

        Add code after super() useful for changes such as forcing UI decimal places
        or manually adding unsupported widgets
        """
        super(MayaScenes, self).updateFromProperties()

    # ------------------------------------
    # UTILS
    # ------------------------------------

    def setPrefVariables(self):
        """Sets prefs global variables from the prefs json file
        self.directory : the current folder location for the assets
        self.uniformIcons : bool whether the thumb icons should be square or non square
        """
        if not self.mayaScenesPrefsData.isValid():  # should be very rare
            output.displayError("The preferences object is not valid")
            return
        self.directory = self.mayaScenesPrefsData["settings"][ac.PREFS_KEY_MAYA_SCENES]
        self.uniformIcons = self.mayaScenesPrefsData["settings"][ac.PREFS_KEY_MAYA_UNIFORM]

    # ------------------------------------
    # RENDERER - AND SEND/RECEIVE ALL TOOLSETS
    # ------------------------------------

    def setRenderer(self, updateAllUIs=True):
        """Filter Maya Scenes by renderer and sets the renderer for all UIs and prefs (optional)

        Uses file suffixes so if set to Arnold then removes someFile_redshift.ma and someFile_renderman.ma from list
        Should switch this over to the info meta data later.

        :param updateAllUIs: If True updates all UIs with the current renderer and sets the renderer in prefs
        :type updateAllUIs: bool
        """
        renderer = self.properties.rendererIconMenu.value

        filteredList = list(DFLT_RNDR_LIST)
        filteredList.pop(filteredList.index(renderer))
        filteredList = [x.lower() for x in filteredList]  # Make all lowercase for suffix filtering

        self.currentWidget().miniBrowser.model().setFilterSuffixList(filteredList)  # Update suffix filtering
        self.currentWidget().miniBrowser.refreshThumbs()  # Do the UI refresh
        if updateAllUIs:  # Send the updated renderer to other UIs
            self.global_changeRenderer()

    def global_changeRenderer(self):
        """Updates all GUIs with the current renderer"""
        self.generalSettingsPrefsData = preference.findSetting(pc.RELATIVE_PREFS_FILE, None)  # refresh data
        toolsets = toolsetui.toolsetsByAttr(attr="global_receiveRendererChange")
        self.generalSettingsPrefsData = elements.globalChangeRenderer(self.properties.rendererIconMenu.value,
                                                                      toolsets,
                                                                      self.generalSettingsPrefsData,
                                                                      pc.PREFS_KEY_RENDERER)

    def global_receiveRendererChange(self, renderer):
        """Receives from other GUIs, changes the renderer when it is changed"""
        self.properties.rendererIconMenu.value = renderer
        self.updateFromProperties()
        self.setRenderer(updateAllUIs=False)  # Refreshes the UI with new renderer

    # ------------------------------------
    # DOTS MENU
    # ------------------------------------

    def uniformIconToggle(self, action):
        """ Toggles the state of the uniform icons

        :param action:
        :type action:
        :return:
        :rtype:
        """
        self.uniformIcons = action.isChecked()
        self.mayaScenesPrefsData["settings"][ac.PREFS_KEY_MAYA_UNIFORM] = self.uniformIcons
        self.mayaScenesPrefsData.save()
        self.refreshThumbs()

    # ------------------------------------
    # REFRESH
    # ------------------------------------

    def refreshPrefs(self):
        self.mayaScenesPrefsData = preference.findSetting(ac.RELATIVE_MAYA_PREFS_FILE, None)  # refresh and update
        if not self.mayaScenesPrefsData.isValid():  # should be very rare
            output.displayError("The preferences object is not valid")
            return False
        return True

    def refreshThumbs(self):
        """Refreshes the GUI """
        self.currentWidget().miniBrowser.refreshThumbs()

    # ------------------------------------
    # PATH HELPER FUNCTIONS
    # ------------------------------------

    def filePath(self, message=True):
        """ Returns the file path of the currently selected thumbnail's corresponding .ma or .mb image eg:

            C:\\Users\\name\\Documents\\zoo_preferences\\assets\\rmaya_scenes\\croc_rig\\animation_croc_walkAndTurn.ma

        :param message: Report any messages to the user?
        :type message: bool
        :return filePath: the full path of the file of the selected thumb, will be "" if none selected
        :rtype filePath: str
        """
        try:
            return self.selectedItem.filePath
        except AttributeError:
            if message:
                output.displayWarning("No thumbnail is selected in the browser.  Please select an image.")
            return ""

    def thumbDirectory(self, message=True):
        """Returns the directory path of the currently selected thumb

        :param message: Report any messages to the user?
        :type message: bool
        :return directory: the path of the directory of the currenlty selected thumb, will be "" if none selected
        :rtype directory: str
        """
        path = self.filePath(message=message)
        if not path:
            return ""
        directory = os.path.dirname(path)
        return directory

    # ------------------------------------
    # OPEN FUNCTIONS AND HELP/BROWSE
    # ------------------------------------

    @toolsetwidget.ToolsetWidget.undoDecorator
    def loadScene(self, assetName=""):
        """ Imports the zooScene asset given the GUI settings
        """
        path = self.filePath()
        if not path:
            return
        dialogResult = saveexportimport.sceneModifiedDialogue()  # Dialog popup save scene?
        if dialogResult == "cancel":
            return
        cmds.file(self.selectedItem.filePath, force=1, options="v=0;", ignoreVersion=1, type="mayaAscii", open=1)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def importScene(self, assetName=""):
        """ Imports the zooScene asset given the GUI settings
        """
        path = self.filePath()
        if not path:
            output.displayWarning("File path not found: {}".format(path))
            return
        if path.lower().endswith(".ma"):
            mayaType = "mayaAscii"
        elif path.lower().endswith(".mb"):
            mayaType = "mayaBinary"
        else:
            output.displayWarning("This path has an unknown file type, not .ma or .mb")
            return
        # todo should handle name conflicts better, filenames are junk it conflicts
        cmds.file(path, force=1, options="v=0;", ignoreVersion=1, type=mayaType, i=1)

    def browseThumbDirectory(self):
        """Opens an OS window to the directory of the currently selected thumb"""
        directory = self.thumbDirectory()
        if not directory:
            return
        filesystem.openDirectory(directory)
        output.displayInfo("Window opened {}".format(directory))

    def openReadme(self):
        """Opens the readMe.pdf stored with the thumbnail selection if it exists
        """
        directory = self.thumbDirectory()
        if not directory:
            return
        readMeFile = os.path.join(directory, "readMe.pdf")
        if not os.path.exists(readMeFile):
            output.displayWarning("No readme.pdf was found for this file.")
            return
        webbrowser.open(readMeFile)
        output.displayInfo("ReadMe.pdf opened {}".format(readMeFile))

    def openHelp(self):
        """The help file url will be stored in a text file in the same directory as the maya file called "helpUrl.txt"

        The contents of that file is the url to the help location.
        """
        directory = self.thumbDirectory()
        if not directory:
            return
        helpTxtFile = os.path.join(directory, "helpUrl.txt")
        if not os.path.exists(helpTxtFile):
            output.displayWarning("No help url was found for this file.")
            return
        url = filesystem.loadFileTxt(helpTxtFile)
        webbrowser.open(url)
        output.displayInfo("Help page opened {}".format(url))

    # ------------------------------------
    # CONNECTIONS
    # ------------------------------------

    def selectionChanged(self, arg1, arg2):
        """Runs when the selection is changed

        :param arg1:
        :type arg1:
        :param arg2:
        :type arg2: zoo.libs.pyqt.extended.imageview.items.BaseItem
        :return:
        :rtype:
        """
        self.selectedItem = arg2  #

    def uiconnections(self):
        """Hooks up the actual button/widgets functionality
        """
        logger.debug("connections()")
        for w in self.widgets():
            # dots menu viewer
            w.miniBrowser.dotsMenu.applyAction.connect(self.loadScene)
            # w.miniBrowser.dotsMenu.createAction.connect(partial(self.setEmbedVisible, vis=True))
            w.miniBrowser.dotsMenu.refreshAction.connect(self.refreshThumbs)
            w.miniBrowser.dotsMenu.uniformIconAction.connect(self.uniformIconToggle)
            w.miniBrowser.dotsMenu.browseAction.connect(self.browseThumbDirectory)
            # Thumbnail viewer
            w.browserModel.doubleClicked.connect(self.loadScene)
            w.browserModel.itemSelectionChanged.connect(self.selectionChanged)
            # Change renderer
            w.rendererIconMenu.actionTriggered.connect(self.setRenderer)
            # Buttons
            w.openSceneBtn.clicked.connect(self.loadScene)
            w.importSceneBtn.clicked.connect(self.importScene)
            w.openReadmeBtn.clicked.connect(self.openReadme)
            w.openHelpBtn.clicked.connect(self.openHelp)
            w.browseDirBtn.clicked.connect(self.browseThumbDirectory)


class AllWidgets(QtWidgets.QWidget):
    """Create all the widgets for all GUIs, compact and advanced etc"""

    def __init__(self, parent=None, properties=None, uiMode=None, toolsetWidget=None, directory=None,
                 uniformIcons=True):
        """Builds the main widgets for the IBL light UIs, no layouts and no connections:

            uiMode - 0 is compact (UI_MODE_COMPACT)
            uiMode - 1 is medium (UI_MODE_MEDIUM)
            ui mode - 2 is advanced (UI_MODE_ADVANCED)

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: qtObject
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: list[dict]
        :param uiMode: 0 is compact ui mode, 1 is medium ui mode, 2 is advanced ui mode
        :type uiMode: int
        :param toolsetWidget: the widget of the toolset
        :type toolsetWidget: qtObject
        :param directory: directory path of the light preset zooScene files
        :type directory: str
        """
        super(AllWidgets, self).__init__(parent=parent)
        self.savedThumbHeight = None
        self.toolsetWidget = toolsetWidget
        self.properties = properties
        self.uiMode = uiMode
        # Thumbnail Viewer --------------------------------------------
        # viewer widget and model
        self.miniBrowser = elements.MiniBrowser(parent=self,
                                                toolsetWidget=self.toolsetWidget,
                                                columns=1,
                                                fixedHeight=382,
                                                uniformIcons=uniformIcons,
                                                itemName="Scene",
                                                applyText="Load Scene",
                                                applyIcon=mayaScenesIcon)

        self.miniBrowser.dotsMenu.setDeleteActive(False)
        self.miniBrowser.dotsMenu.setCreateActive(False)
        self.miniBrowser.dotsMenu.setRenameActive(False)
        self.miniBrowser.dotsMenu.setDirectoryActive(False)
        self.miniBrowser.filterMenu.setEnabled(False)
        self.miniBrowser.infoButton.setEnabled(False)

        self.miniBrowser.filterMenu.hide()
        self.miniBrowser.infoButton.hide()

        self.browserModel = mayafilemodel.MayaFileModel(self.miniBrowser,
                                                        directory=directory,
                                                        chunkCount=200,
                                                        uniformIcons=uniformIcons)
        self.miniBrowser.setModel(self.browserModel)
        self.resizerWidget = ToolsetResizer(toolsetWidget=self.toolsetWidget, target=self.miniBrowser)
        # Open File Button --------------------------------------
        tooltip = "Opens the selected file (also double-click)."
        self.openSceneBtn = elements.styledButton("Open",
                                                  icon="checkMark",
                                                  toolTip=tooltip,
                                                  style=uic.BTN_DEFAULT)
        # Import File Button --------------------------------------
        tooltip = "Imports the selected file (also double-click)."
        self.importSceneBtn = elements.styledButton("Import",
                                                    icon="arrowCircleDown",
                                                    toolTip=tooltip,
                                                    style=uic.BTN_DEFAULT)
        # Open File Button --------------------------------------
        tooltip = "Reference the selected file (also double-click)."
        self.referenceSceneBtn = elements.styledButton("Reference",
                                                       icon="checkMark",
                                                       toolTip=tooltip,
                                                       style=uic.BTN_DEFAULT)
        self.referenceSceneBtn.hide()
        # Open Readme Button --------------------------------------
        tooltip = "Opens the readMe.pdf for the selected file."
        self.openReadmeBtn = elements.styledButton("",
                                                   icon="information",
                                                   toolTip=tooltip,
                                                   style=uic.BTN_DEFAULT)
        # Open Help Button --------------------------------------
        tooltip = "Opens the help file for the selected file."
        self.openHelpBtn = elements.styledButton("",
                                                 icon="help",
                                                 toolTip=tooltip,
                                                 style=uic.BTN_DEFAULT)
        # Open Directory Browse Button --------------------------------------
        tooltip = "Browse the scene file/s on disk for the selected file."
        self.browseDirBtn = elements.styledButton("",
                                                  icon="globe",
                                                  toolTip=tooltip,
                                                  style=uic.BTN_DEFAULT)
        # Renderer Button --------------------------------------
        toolTip = "Show only files of this renderer type, note that files unrelated to a renderer are kept. \n\n" \
                  "Files are excluded by their file suffix `*_redshift` \n" \
                  "Renderer of the file suffix should be all lowercase."
        self.rendererIconMenu = elements.iconMenuButtonCombo(DFLT_RNDR_MODES,
                                                             self.properties.rendererIconMenu.value,
                                                             toolTip=toolTip)
        # self.rendererIconMenu.setEnabled(False)

    def embedWindowVisChanged(self, visibility):
        self.toolsetWidget.updateTree(delayed=True)


class GuiCompact(AllWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_COMPACT, toolsetWidget=None, directory=None,
                 uniformIcons=True):
        """Builds the compact version of GUI, sub classed from AllWidgets() which creates the widgets:

            default uiMode - 1 is compact (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: qtObject
        :param properties: Special dictionary which tracks the properties of each widget for the GUI
        :type properties: list[dict]
        :param uiMode: The UI mode to build, either UI_MODE_COMPACT = 0 or UI_MODE_ADVANCED = 1
        :type uiMode: int
        :param toolsetWidget: The instance of the toolsetWidget class, needed for setting properties.
        :type toolsetWidget: object
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties,
                                         uiMode=uiMode, toolsetWidget=toolsetWidget, directory=directory,
                                         uniformIcons=uniformIcons)
        # Main Layout
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINTOPPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=0)
        # Renderer layout
        rendererLayout = elements.hBoxLayout()
        rendererLayout.addWidget(self.openSceneBtn, 10)
        rendererLayout.addWidget(self.importSceneBtn, 10)
        rendererLayout.addWidget(self.openReadmeBtn, 1)
        rendererLayout.addWidget(self.openHelpBtn, 1)
        rendererLayout.addWidget(self.browseDirBtn, 1)
        rendererLayout.addWidget(self.rendererIconMenu, 1)
        # Add to main layout
        mainLayout.addWidget(self.miniBrowser)
        mainLayout.addWidget(self.resizerWidget)
        mainLayout.addLayout(rendererLayout)
        mainLayout.addStretch(1)
