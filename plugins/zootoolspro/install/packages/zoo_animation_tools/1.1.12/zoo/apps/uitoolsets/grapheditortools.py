""" ---------- General Graph Editor Tools -------------
Randomize animation keyframe UI.

Author: Andrew Silke
"""

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.core.util import env

if env.isInMaya():
    from zoo.libs.maya.cmds.animation import generalanimation, animconstants

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

CYCLE_BUTTON_MODES = [("loopAbc", "Cycle Both Pre And Post"), ("loopAbc", "Cycle Pre Only"),
                      ("loopAbc", "Cycle Post Only")]


class GraphEditorTools(toolsetwidget.ToolsetWidget):
    id = "graphEditorTools"
    info = "Assorted animation Graph Editor tools."
    uiData = {"label": "Graph Editor Toolbox",
              "icon": "graphEditor",
              "tooltip": "Assorted animation Graph Editor tools.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-graph-editor-toolbox/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        pass

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget(), self.initAdvancedWidget()]

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
        return super(GraphEditorTools, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(GraphEditorTools, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def snapKeysWholeFrames(self):
        generalanimation.snapKeysWholeFrames()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def snapKeysCurrent(self):
        generalanimation.snapKeysCurrent()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def eulerFilter(self):
        generalanimation.eulerFilter()

    def cycleModeMenuClicked(self):
        """Convenience as avoids undo decorator inner return func(*args, **kwargs) issue"""
        self.cycleAnimation()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def cycleAnimation(self):
        """Cycles the animation either pre or post or both"""
        cyclePrePost = self.properties.cycleAnimationMenuBtn.value
        if cyclePrePost == CYCLE_BUTTON_MODES[0][1]:  # Pre post
            pre = True
            post = True
        elif cyclePrePost == CYCLE_BUTTON_MODES[1][1]:  # Pre only
            pre = True
            post = False
        elif cyclePrePost == CYCLE_BUTTON_MODES[2][1]:  # Post only
            pre = False
            post = True
        # Do the cycle ---------------------
        generalanimation.cycleAnimation(cycleMode=self.properties.cycleCombo.value,
                                        pre=pre,
                                        post=post,
                                        displayInfinity=True)

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def removeCycleAnimation(self):
        generalanimation.removeCycleAnimation()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def toggleInfinity(self):
        generalanimation.toggleInfinity()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def hideInfinity(self):
        generalanimation.showInfinity(False)

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def selObjGraph(self):
        generalanimation.selObjGraph()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def timeToKey(self):
        generalanimation.timeToKey()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def insertKey(self):
        generalanimation.insertKey()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def animHold(self):
        generalanimation.animHold()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def bakeKeys(self):
        generalanimation.bakeKeys()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def copyKeys(self):
        generalanimation.copyKeys()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def pasteKeys(self):
        generalanimation.pasteKeys()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            # Cycle Menu ----------------------------
            widget.cycleAnimationMenuBtn.actionTriggered.connect(self.cycleModeMenuClicked)
            # Buttons -------------------------
            widget.toggleInfinityBtn.clicked.connect(self.toggleInfinity)
            widget.removeCycleAnimationBtn.clicked.connect(self.removeCycleAnimation)
            widget.snapKeysCurrentBtn.clicked.connect(self.snapKeysCurrent)
            widget.snapKeysWholeFramesBtn.clicked.connect(self.snapKeysWholeFrames)
            widget.eulerFilterBtn.clicked.connect(self.eulerFilter)
            widget.selObjGraphBtn.clicked.connect(self.selObjGraph)
            widget.timeToKeyBtn.clicked.connect(self.timeToKey)
            widget.insertKeyBtn.clicked.connect(self.insertKey)
            widget.bakeKeysBtn.clicked.connect(self.bakeKeys)
            widget.animHoldBtn.clicked.connect(self.animHold)
            widget.copyKeysBtn.clicked.connect(self.copyKeys)
            widget.pasteKeysBtn.clicked.connect(self.pasteKeys)


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
        # Cycle Combo ---------------------------------------
        toolTip = "Cycles the selected objects for both pre and post. \n" \
                  "Zoo Hotkey: alt o (Regular Cycle)"
        self.cycleCombo = elements.ComboBoxRegular(label="Cycle Curves",
                                                   labelRatio=16,
                                                   boxRatio=23,
                                                   items=animconstants.GRAPH_CYCLE_LONG,
                                                   parent=parent,
                                                   toolTip=toolTip)
        self.cycleAnimationMenuBtn = elements.iconMenuButtonCombo(CYCLE_BUTTON_MODES,
                                                                  defaultMenuItem=CYCLE_BUTTON_MODES[0][0],
                                                                  toolTip=toolTip)
        # Toggle Infinity ---------------------------------
        toolTip = "Toggles the infinity display in the graph editor. \n" \
                  "Zoo Hotkey: shift i"
        self.toggleInfinityBtn = elements.AlignedButton("Toggle Infinity",
                                                        icon="infinite",
                                                        toolTip=toolTip)
        # Remove Cycle ---------------------------------
        toolTip = "Removes any cycling animation on the selected objects for both pre and post. \n" \
                  "Zoo Hotkey: ctrl alt o"
        self.removeCycleAnimationBtn = elements.AlignedButton("Remove Cycle",
                                                              icon="removeLoop",
                                                              toolTip=toolTip)
        # Snap Key Retain ----------------------------------
        toolTip = "Snaps the selected keys to whole frames. \n" \
                  "Zoo Hotkey: shift alt o"
        self.snapKeysWholeFramesBtn = elements.AlignedButton("Snap Whole Frames",
                                                             icon="magnet",
                                                             toolTip=toolTip)
        # Snap To Current Time ---------------------------------
        toolTip = "Snaps the selected graph keys to the current time. \n" \
                  "Zoo Hotkey: ctrl alt a"
        self.snapKeysCurrentBtn = elements.AlignedButton("Snap Keys To Current",
                                                         icon="snapTime",
                                                         toolTip=toolTip)
        # Time To Selected Key ---------------------------------
        toolTip = "Moves the time slider to the closest selected keyframe. \n" \
                  "Zoo Hotkey: shift alt a"
        self.timeToKeyBtn = elements.AlignedButton("Time To Selected Key",
                                                   icon="timeToSelected",
                                                   toolTip=toolTip)
        # Euler Filter Keyframes ----------------------------------
        toolTip = "Euler Filter for de-tangling gimbal aligned curve rotations. \n" \
                  "Zoo Hotkey: ctrl shift alt g"
        self.eulerFilterBtn = elements.AlignedButton("Euler Filter",
                                                     icon="rotateManipulator",
                                                     toolTip=toolTip)
        # Select Object From Graph Curve ---------------------------------
        toolTip = "Select an object from a graph curve selection. \n" \
                  "Zoo Hotkey: shift ctrl alt a"
        self.selObjGraphBtn = elements.AlignedButton("Sel Obj From FCurve",
                                                     icon="selectObject",
                                                     toolTip=toolTip)
        # Insert Key Tool ----------------------------------
        toolTip = "Maya's Insert Key Tool.\n" \
                  "Inserts a keyframe at the current time without affecting graph curves.  \n" \
                  "Select animation curve/s, or will work on all keyed attributes. \n" \
                  "Zoo & Maya Hotkey 1: i (hold) middle click drag on curve \n" \
                  "Zoo & Maya Hotkey 2: alt i"
        self.insertKeyBtn = elements.AlignedButton("Insert Key Tool",
                                                   icon="insertKey",
                                                   toolTip=toolTip)

        # Bake ----------------------------------
        toolTip = "Bake animation for every frame on the selected objects. \n" \
                  "Works on the playback range \n" \
                  "Zoo Hotkey: shift alt b"
        self.bakeKeysBtn = elements.AlignedButton("Bake Playback Range",
                                                  icon="bake",
                                                  toolTip=toolTip)
        # Make Animation Hold ---------------------------------
        toolTip = "Make an animation hold. \n" \
                  "Place the timeline between two keys and run. \n" \
                  "The first key will be copied to the second with flat tangents. \n" \
                  "Zoo Hotkey: alt a"
        self.animHoldBtn = elements.AlignedButton("Make Anim Hold",
                                                  icon="animHold",
                                                  toolTip=toolTip)
        # Copy Keyframes ----------------------------------
        toolTip = "Copy Keyframes in the Graph Editor. \n" \
                  "Zoo Hotkey: ctrl c"
        self.copyKeysBtn = elements.AlignedButton("Copy Keyframes",
                                                  icon="copy",
                                                  toolTip=toolTip)
        # Paste Keyframes ----------------------------------
        toolTip = "Paste Keyframes in the Graph Editor. \n" \
                  "Merge style paste mode. \n" \
                  "Zoo Hotkey: ctrl v"
        self.pasteKeysBtn = elements.AlignedButton("Paste Keyframes",
                                                   icon="paste",
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
                                         spacing=uic.SREG)
        # Cycle Combo Layout -----------------------------
        cycleComboLayout = elements.hBoxLayout(parent)
        cycleComboLayout.addWidget(self.cycleCombo, 20)
        cycleComboLayout.addWidget(self.cycleAnimationMenuBtn, 1)
        # Grid Layout ----------------------------------------------------------
        gridTopLayout = elements.GridLayout(spacing=uic.SPACING)
        row = 0
        gridTopLayout.addLayout(cycleComboLayout, row, 0, 1, 2)
        row += 1
        gridTopLayout.addWidget(self.toggleInfinityBtn, row, 0)
        gridTopLayout.addWidget(self.removeCycleAnimationBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.snapKeysCurrentBtn, row, 0)
        gridTopLayout.addWidget(self.snapKeysWholeFramesBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.eulerFilterBtn, row, 0)
        gridTopLayout.addWidget(self.selObjGraphBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.timeToKeyBtn, row, 0)
        gridTopLayout.addWidget(self.insertKeyBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.bakeKeysBtn, row, 0)
        gridTopLayout.addWidget(self.animHoldBtn, row, 1)
        # Add To Main Layout ---------------------------------------
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
        # Cycle Combo Layout -----------------------------
        cycleComboLayout = elements.hBoxLayout(parent)
        cycleComboLayout.addWidget(self.cycleCombo, 20)
        cycleComboLayout.addWidget(self.cycleAnimationMenuBtn, 1)
        # Grid Layout ----------------------------------------------------------
        gridTopLayout = elements.GridLayout(spacing=uic.SPACING)
        row = 0
        gridTopLayout.addLayout(cycleComboLayout, row, 0, 1, 2)
        row += 1
        gridTopLayout.addWidget(self.toggleInfinityBtn, row, 0)
        gridTopLayout.addWidget(self.removeCycleAnimationBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.snapKeysCurrentBtn, row, 0)
        gridTopLayout.addWidget(self.snapKeysWholeFramesBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.eulerFilterBtn, row, 0)
        gridTopLayout.addWidget(self.selObjGraphBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.timeToKeyBtn, row, 0)
        gridTopLayout.addWidget(self.insertKeyBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.bakeKeysBtn, row, 0)
        gridTopLayout.addWidget(self.animHoldBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.copyKeysBtn, row, 0)
        gridTopLayout.addWidget(self.pasteKeysBtn, row, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(gridTopLayout)
