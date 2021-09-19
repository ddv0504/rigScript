from zoovendor.Qt import QtWidgets


from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.core.util import env
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

if env.isInMaya():
    import maya.mel as mel
    from zoo.libs.maya.utils import general

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class ManageNodes(toolsetwidget.ToolsetWidget):
    id = "manageNodes"
    info = "Misc node tools."
    uiData = {"label": "Manage Nodes Plugins",
              "icon": "nodeTools",
              "tooltip": "Miscellaneous node tools",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-manage-nodes/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        pass

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self)
        return self.compactWidget

    def initAdvancedWidget(self):
        """Builds the Advanced GUI (self.advancedWidget) """
        self.advancedWidget = GuiAdvanced(parent=self, properties=self.properties, toolsetWidget=self)
        return self.advancedWidget

    def postContentSetup(self):
        """Last of the initialize code"""
        self.uiConnections()

    def defaultAction(self):
        """Double Click
        Double clicking the tools toolset icon will run this method
        Be sure "defaultActionDoubleClick": True is set inside self.uiData (meta data of this class)"""
        pass

    def currentWidget(self):
        """ Currently active widget

        :return:
        :rtype: GuiAdvanced or GuiCompact
        """
        return super(ManageNodes, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(ManageNodes, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    def lockSelectedNodes(self):
        """Locks the selected maya nodes/objects"""
        general.lockSelectedNodes()

    def unlockSelectedNodes(self):
        """Unlocks the selected maya nodes/objects"""
        general.lockSelectedNodes(unlock=True)

    def deleteTurtle(self):
        """Removes the turtle plugin from the scene and deletes the shelf"""
        general.deleteTurtlePluginScene(removeShelf=True, message=True)

    def openPluginManager(self):
        """Opens Maya's plugin manager"""
        mel.eval("pluginWin")

    def deleteUnusedNodes(self):
        """Deletes all unused nodes in the scene"""
        general.deleteUnknownNodes()

    def deleteUnusedPlugins(self):
        """Deletes all unused nodes in the scene"""
        general.removeUnknownPlugins()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.deleteUnknownNodesBtn.clicked.connect(self.deleteUnusedNodes)
            widget.deleteUnknownPluginsBtn.clicked.connect(self.deleteUnusedPlugins)
            widget.openPluginManagerBtn.clicked.connect(self.openPluginManager)
            widget.deleteTurtleBtn.clicked.connect(self.deleteTurtle)
            widget.lockSelectedNodesBtn.clicked.connect(self.lockSelectedNodes)
            widget.unlockSelectedNodesBtn.clicked.connect(self.unlockSelectedNodes)


class GuiWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None, properties=None, uiMode=None, toolsetWidget=None):
        """Builds the main widgets for all GUIs

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        :param uiMode: 0 is compact ui mode, 1 is advanced ui mode
        :type uiMode: int
        """
        super(GuiWidgets, self).__init__(parent=parent)
        self.properties = properties
        # Unlock Selected Nodes Button ---------------------------------------
        toolTip = "Unlocks selected nodes/objects in the scene."
        self.unlockSelectedNodesBtn = elements.styledButton("Unlock Selected Nodes",
                                                            "unlock",
                                                            toolTip=toolTip,
                                                            style=uic.BTN_LABEL_SML)
        # Lock Selected Nodes Button ---------------------------------------
        toolTip = "Locks selected nodes or objects in the scene so that they cannot be deleted."
        self.lockSelectedNodesBtn = elements.styledButton("Lock Selected Nodes",
                                                          "lock",
                                                          toolTip=toolTip,
                                                          style=uic.BTN_LABEL_SML)
        # Open Maya Plugin Manager Button ---------------------------------------
        toolTip = "Opens Maya's Plugin Manager."
        self.openPluginManagerBtn = elements.styledButton("Open Plug-In Manager",
                                                          "window",
                                                          toolTip=toolTip,
                                                          style=uic.BTN_LABEL_SML)
        # Delete Turtle Plugin Button ---------------------------------------
        toolTip = "Deletes the Turtle plugin from the scene, \n" \
                  "unloads the plugin and deletes the shelf."
        self.deleteTurtleBtn = elements.styledButton("Delete Turtle Plugin",
                                                     "turtlePlugin",
                                                     toolTip=toolTip,
                                                     style=uic.BTN_LABEL_SML)
        # Delete Unused Nodes Button ---------------------------------------
        toolTip = "Deletes all unknown nodes in the scene. \n" \
                  "Unknown nodes are usually from renderers that are not installed, \n" \
                  "or other unused plugins. \n\n" \
                  "Will stop the `Unkown Node` popup window as scenes are opened."
        self.deleteUnknownNodesBtn = elements.styledButton("Delete Unknown Nodes",
                                                           "trash",
                                                           toolTip=toolTip,
                                                           style=uic.BTN_LABEL_SML)
        # Delete Unused Plugins Button ---------------------------------------
        toolTip = "Deletes all unknown plugins in the scene. \n" \
                  "Unknown plugins are usually from renderers that are not installed, \n" \
                  "or other unused plugins. \n\n" \
                  "Will stop the `Unkown Node` popup window as scenes are opened."
        self.deleteUnknownPluginsBtn = elements.styledButton("Delete Unknown Plugins",
                                                             "trash",
                                                             toolTip=toolTip,
                                                             style=uic.BTN_LABEL_SML)


class GuiCompact(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_COMPACT, toolsetWidget=None):
        """Adds the layout building the compact version of the GUI:

            default uiMode - 0 is advanced (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                         toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Grid Layout ---------------------------------------
        gridLayout = elements.GridLayout(hSpacing=uic.SVLRG)
        gridLayout.addWidget(self.lockSelectedNodesBtn, 0, 0)
        gridLayout.addWidget(self.unlockSelectedNodesBtn, 0, 1)
        gridLayout.addWidget(self.openPluginManagerBtn, 1, 0)
        gridLayout.addWidget(self.deleteTurtleBtn, 1, 1)
        gridLayout.addWidget(self.deleteUnknownNodesBtn, 2, 0)
        gridLayout.addWidget(self.deleteUnknownPluginsBtn, 2, 1)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(gridLayout)


class GuiAdvanced(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_ADVANCED, toolsetWidget=None):
        """Adds the layout building the advanced version of the GUI:

            default uiMode - 1 is advanced (UI_MODE_ADVANCED)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiAdvanced, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                          toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Grid Layout ---------------------------------------
        gridLayout = elements.GridLayout(hSpacing=uic.SVLRG)
        gridLayout.addWidget(self.lockSelectedNodesBtn, 0, 0)
        gridLayout.addWidget(self.unlockSelectedNodesBtn, 0, 1)
        gridLayout.addWidget(self.openPluginManagerBtn, 1, 0)
        gridLayout.addWidget(self.deleteTurtleBtn, 1, 1)
        gridLayout.addWidget(self.deleteUnknownNodesBtn, 2, 0)
        gridLayout.addWidget(self.deleteUnknownPluginsBtn, 2, 1)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(gridLayout)
