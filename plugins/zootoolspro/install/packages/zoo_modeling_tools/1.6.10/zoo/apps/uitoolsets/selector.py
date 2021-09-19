""" ---------- Selector -------------
A tool for select functions

Author: Andrew Silke
"""

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.libs.maya.cmds.objutils import selection

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class Selector(toolsetwidget.ToolsetWidget):
    id = "selector"
    info = "Template file for building new GUIs."
    uiData = {"label": "Select",
              "icon": "cursorSelect",
              "tooltip": "Template file for building new GUIs.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-select/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        pass

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]  # self.initAdvancedWidget()

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
        return super(Selector, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(Selector, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    def randomSelection(self):
        """Selects randomly from the current selection
        """
        selection.randomSelection(self.properties.selectRandomFloat.value)

    def growSelection(self):
        """Grow selection
        """
        selection.growSelection()

    def shrinkSelection(self):
        """Shrink selection
        """
        selection.shrinkSelection()

    def invertSelection(self):
        """Selects all children of the current selection
        """
        selection.invertSelection()

    def selectHierarchy(self):
        """Selects all children of the current selection
        """
        selection.selectHierarchy()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.randomSelectBtn.clicked.connect(self.randomSelection)
            widget.growSelectionBtn.clicked.connect(self.growSelection)
            widget.shrinkSelectionBtn.clicked.connect(self.shrinkSelection)
            widget.selectHierarchyBtn.clicked.connect(self.selectHierarchy)
            widget.invertSelectionBtn.clicked.connect(self.invertSelection)


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
        # Label and Textbox ---------------------------------------
        tooltip = "Select random objects or components and run. \n" \
                  "  - 50 will randomly select 50% of the current selection. \n" \
                  "  - 10 will randomly select 10% of the current selection."
        self.selectRandomFloat = elements.FloatEdit(label="Percentage",
                                                    editText=50,
                                                    toolTip=tooltip,
                                                    smallSlideDist=0.1,
                                                    slideDist=0.5,
                                                    largeSlideDist=5.0)
        # Randomize Button ---------------------------------------
        self.randomSelectBtn = elements.AlignedButton("Select Random",
                                                      icon="randomSelect",
                                                      toolTip=tooltip)
        # Grow Selection ---------------------------------
        toolTip = "Grows the current component selection. \n" \
                  "Select a vertex, face, edge, or UV and run to grow to surrounding components. "
        self.growSelectionBtn = elements.AlignedButton("Grow Selection",
                                                       icon="grow",
                                                       toolTip=toolTip)
        # Shrink Selection ---------------------------------
        toolTip = "Shrinks the current component selection. \n" \
                  "Select a vertex, face, edge, or UV and run to shrink the selection. "
        self.shrinkSelectionBtn = elements.AlignedButton("Shrink Selection",
                                                         icon="shrink",
                                                         toolTip=toolTip)
        # Select Hierarchy ---------------------------------
        toolTip = "Adds children of the currently selected objects to the selection."
        self.selectHierarchyBtn = elements.AlignedButton("Select Hierarchy",
                                                         icon="hierarchy",
                                                         toolTip=toolTip)
        # Invert Selection ---------------------------------
        toolTip = "Inverts the current selection"
        self.invertSelectionBtn = elements.AlignedButton("Invert Selection",
                                                         icon="invert",
                                                         toolTip=toolTip)


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
                                         spacing=uic.SPACING)
        # Grid Layout ----------------------------------------------------------
        gridTopLayout = elements.GridLayout(spacing=uic.SPACING)
        row = 0
        gridTopLayout.addWidget(self.selectRandomFloat, row, 0)
        gridTopLayout.addWidget(self.randomSelectBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.growSelectionBtn, row, 0)
        gridTopLayout.addWidget(self.shrinkSelectionBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.invertSelectionBtn, row, 0)
        gridTopLayout.addWidget(self.selectHierarchyBtn, row, 1)
        gridTopLayout.setColumnStretch(0, 1)
        gridTopLayout.setColumnStretch(1, 1)
        # Add To Main Layout ---------------------
        mainLayout.addLayout(gridTopLayout)


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
        # Add To Main Layout ---------------------------------------
        mainLayout.addWidget(self.selectRandomFloat)
        mainLayout.addWidget(self.randomSelectBtn)
