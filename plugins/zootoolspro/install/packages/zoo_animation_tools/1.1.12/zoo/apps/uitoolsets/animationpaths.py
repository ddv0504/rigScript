""" ---------- Animation Paths -------------

- Creates a CV Curve from an animated object's path
- Creates objects from an animated object's path
- Motion Path Button
- Ghosting Editor Button

Author: Andrew Silke
Credit:  Cleaned up faster code from the original script by Delano Athias
Credit URL: https://www.delanimation.com/tutorials-1/2020/1/2/generating-curves-from-motion-trails-in-maya
"""

from zoovendor.Qt import QtWidgets

from zoo.libs.maya.utils import mayaenv

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.libs.maya.cmds.animation import motiontrail, generalanimation

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class AnimationPaths(toolsetwidget.ToolsetWidget):
    id = "animationPaths"
    info = "A UI for handling motion paths and cv curves."
    uiData = {"label": "Animation Paths",
              "icon": "motionTrail",
              "tooltip": "Template file for building new GUIs.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-animation-paths/"}

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
        return super(AnimationPaths, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(AnimationPaths, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def cvCurveFromObjAnim(self):
        """Creates CV Curves from an animated object
        """
        motiontrail.cvCurveFromObjAnimationSelected(cvEveryFrame=self.properties.cvsPerFrameFloat.value)

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def cloneObjsFromAnim(self):
        """Creates objects from an animated object
        """
        motiontrail.cloneObjsFromAnimationSelected(objToFrame=self.properties.objectsPerFrameFloat.value)

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def createMotionTrail(self):
        generalanimation.createMotionTrail()

    @toolsetwidget.toolsetwidgetmaya.undoDecorator
    def openGhostEditor(self):
        if mayaenv.mayaVersion() >= 2022:  # Should be already hidden in 2020 and below.
            generalanimation.openGhostEditor()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.cvCurveFromKeysBtn.clicked.connect(self.cvCurveFromObjAnim)
            widget.objectsFromKeysBtn.clicked.connect(self.cloneObjsFromAnim)
            widget.motionPathBtn.clicked.connect(self.createMotionTrail)
            widget.openGhostEditorBtn.clicked.connect(self.openGhostEditor)


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
        # CVs Per Frame Float Box ---------------------------------------
        tooltip = "Creates a CV NURBS Curve from the selected object/s motion paths. \n" \
                  "Uses the Playback Range in the Time Slider. \n" \
                  "CVs are placed once every `x` frames."
        self.cvsPerFrameFloat = elements.FloatEdit(label="CVs/Frame Ratio",
                                                   editText=1.0,
                                                   toolTip=tooltip)
        # CV Curve From Keys ---------------------------------------
        self.cvCurveFromKeysBtn = elements.AlignedButton("CV Curve From Anim",
                                                         icon="splineCVs",
                                                         toolTip=tooltip)
        # Object/Frame Float Box ---------------------------------------
        tooltip = "Duplicates the selected object/s along their animation paths. \n" \
                  "Uses the Playback Range in the Time Slider. \n" \
                  "Objects are placed once every `x` frames."
        self.objectsPerFrameFloat = elements.FloatEdit(label="Obj/Frame Ratio",
                                                       editText=10.0,
                                                       toolTip=tooltip)
        # Objects From Keys ---------------------------------------
        self.objectsFromKeysBtn = elements.AlignedButton("Objects From Anim",
                                                         icon="objectsOnCurve",
                                                         toolTip=tooltip)
        # MotionPath ---------------------------------------
        tooltip = "Creates a motion trail on the selected object.\n" \
                  "Uses the current Playback Range in the Time Slider\n" \
                  "Zoo Hotkey: shift alt {"
        self.motionPathBtn = elements.AlignedButton("Create Motion Path",
                                                    icon="motionTrail",
                                                    toolTip=tooltip)
        # CV Curve From Keys ---------------------------------------
        tooltip = "Opens Maya's Ghost Editor Window. \n" \
                  "Uses the current Playback Range in the Time Slider \n" \
                  "Zoo Hotkey: shift alt }"
        self.openGhostEditorBtn = elements.AlignedButton("Open Ghost Editor",
                                                         icon="ghosting",
                                                         toolTip=tooltip)
        if mayaenv.mayaVersion() < 2022:
            self.openGhostEditorBtn.setVisible(False)


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
        # CV Curve Layout ---------------------------------------
        cvCurveLayout = elements.hBoxLayout(self, spacing=uic.SPACING)
        cvCurveLayout.addWidget(self.cvsPerFrameFloat, 1)
        cvCurveLayout.addWidget(self.cvCurveFromKeysBtn, 1)
        # Object Clone Layout ---------------------------------------
        objectLayout = elements.hBoxLayout(self, spacing=uic.SPACING)
        objectLayout.addWidget(self.objectsPerFrameFloat, 1)
        objectLayout.addWidget(self.objectsFromKeysBtn, 1)
        # Motion Path Layout ---------------------------------------
        motionPathLayout = elements.hBoxLayout(self, spacing=uic.SPACING)
        motionPathLayout.addWidget(self.motionPathBtn, 1)
        motionPathLayout.addWidget(self.openGhostEditorBtn, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(cvCurveLayout)
        mainLayout.addLayout(objectLayout)
        mainLayout.addLayout(motionPathLayout)


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
        mainLayout.addWidget(self.cvsPerFrameFloat)
        mainLayout.addWidget(self.cvCurveFromKeysBtn)
