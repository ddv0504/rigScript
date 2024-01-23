### See the file "LICENSE.txt" for the full license governing this code.

from maya.app.flux.ae.Template import Template
from maya.app.flux.ae.Custom import Custom
from maya.app.flux.imports import *
import maya.app.flux.core as fx
from maya.app.flux.core import pix
import maya.app.flux.ae.utils as aeUtils
import maya.cmds as cmds

from copy import deepcopy
import weakref
import proSetsAPI
import proSetsUI as psui

# The PromptWrapper is used as a way to get variables
# into and out of a cmds.layoutDialog() which by default
# takes no arguements and returns only predefined strings.
class PromptWrapper(object):
    def __init__(self, node):
        self.node = node
        self.reply = None
        self.message = None

    def createHistoryPrompt(self):
        if not self.node:
            return

        def selectionChanged():
            self.reply = cmds.textScrollList('connectHistoryPromptList', query=True, selectItem=True)[0]

        def historyPromptUI():
            cmds.columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
            cmds.text(l='Select the history node to use.')
            selection = cmds.ls(sl=True)

            history = cmds.listHistory(self.node)
            print (history)
            
            nodeList = []
            for node in history:
                attrs = cmds.listAttr(node, write=True)
                for attr in attrs:
                    if 'components' in attr.lower():
                        nodeList.append(node)
                        break
            if len(nodeList):
                cmds.textScrollList('connectHistoryPromptList', numberOfRows=5, allowMultiSelection=False,append=nodeList, selectCommand=selectionChanged)
                cmds.button(l='Continue', c='import maya.cmds as cmds;cmds.layoutDialog( dismiss="Continue")' )
            else:
                cmds.text(l='Something went wrong.')

            cmds.button(l='Cancel', c='import maya.cmds as cmds;cmds.layoutDialog( dismiss="Cancel" )' )
        
        self.message = cmds.layoutDialog(ui=historyPromptUI)


class AEproSetTemplate(Template):
    def buildUI(self, nodeName):
        self.addCustom(PSCustom(nodeName))

class PSCustom(Custom):
    def buildUI(self, nodeName):
        self.pluginName = 'proSet'

        self.toolbar = fx.widgetWithLayout('H', pix(2), pix(5),pix(2),pix(5),pix(2))
        self.toolbar.setAutoFillBackground(True)
        self.toolbar.setFixedHeight(pix(30))
        fx.setWidgetBackgroundColor(self.toolbar, [73,73,73])
        
        self.mainIcon = qt.QLabel()
        self.mainIcon.setPixmap(fx.getPixmap('out_proSet'))
        self.toolbar.layout().addSpacing(pix(2))
        self.toolbar.layout().addWidget(self.mainIcon)

        self.titleLabel = qt.QLabel('ProSet')
        self.toolbar.layout().addWidget(self.titleLabel)

        self.toolbar.layout().addStretch()

        #
        # Disabled as part of #37 (too many similar features).
        #
        #self.showAllBtn = fx.ImageButton('ProSet_Show')
        #self.showAllBtn.clicked.connect(self.showAllClicked)
        #self.toolbar.layout().addWidget(self.showAllBtn)

        self.enableBtn = fx.ImageButton('out_MASH_Enable')
        self.enableBtn.isOn = True
        self.enableBtn.clicked.connect(self.enableClicked)
        self.enableBtn.setToolTip('Enable/Disable the ProSet.')

        self.toolbar.layout().addWidget(self.enableBtn)

        self.addWidget(self.toolbar)

        self.dropWidget = psui.DropListWidget(psui.CustomListWidget(), 'Modelling tools:', "Drag a mesh, or modelling node in here.")
        self.dropWidget.dropped.connect(self.uiDroppedNode)
        self.dropWidget.reorder.connect(self.uiReorderNodes)
        self.dropWidget.updateView.connect(self.updateNodes)
        self.dropWidget.buttonClicked.connect(self.uiButtonClicked)
        self.dropWidget.selected.connect(self.uiSelected)
        self.addWidget(self.dropWidget)

        self.addEnum('componentMode', label='Component Mode')
        self.addSlider('growSelection', label='Grow Selection')
        self.addCheckbox('percentage', label='Percentage')
        self.addCheckbox('enableBoundaryComponents', label='Add Boundary Components', annotation='Select components on a mesh border (e.g. those around a hole).')
        self.addCheckbox('invertComponents', label='Invert Components')

        with self.frameLayout('Modulus', False):
            self.addCheckbox('enableModulus', label='Use Modulus', annotation='Select every nth component.')
            self.modulus = self.addSlider('modulus', label='Modulus')

        with self.frameLayout('Shader', False):
            self.addEnum('mapMode', label='Mode')
            self.addColor('map', label='Shader')

        with self.frameLayout('Falloffs', False):
            self.falloffDropWidget = psui.DropListWidget(psui.FalloffListWidget(), 'Falloff objects:', "Right click to add a falloff object.")
            self.falloffDropWidget.dropped.connect(self.uiDroppedFalloffNode)
            self.falloffDropWidget.updateView.connect(self.updateFalloffs)
            self.addWidget(self.falloffDropWidget)
        
        with self.frameLayout('Component Size', False):
            self.enableComponentSize = self.addCheckbox('enableComponentSize', label='Use Component Size')
            self.sizeMode = self.addCheckbox('componentSizeMode', label='Size Mode')
            self.faceAreaMin = self.addSlider('faceAreaMin', label='Min. Face Area')
            self.faceAreaMax = self.addSlider('faceAreaMax', label='Max. Face Area')
            self.edgeLengthMin = self.addSlider('edgeLengthMin', label='Min. Edge Length')
            self.edgeLengthMax = self.addSlider('edgeLengthMax', label='Max. Edge Length')
            self.componentSpaceMode = self.addEnum('componentSpaceMode', label='Space Mode')

        with self.frameLayout('Normals', False):
            self.normalAngleMode = self.addEnum('normalAngleMode', label='Normal Mode')
            self.growResultMin = self.addSlider('growResultMin', label='Grow Result Min.')
            self.growResultMax = self.addSlider('growResultMax', label='Grow Result Max.')
            self.normalAngle = self.addVector('normalAngle', label='Normal Angle')
            self.useSmoothEdges = self.addCheckbox('edgeMode', label='Edge Mode')

        with self.frameLayout('Random', False):
            self.addSlider('randomSeed', label='Random Seed')
            self.addSlider('randomComponents', label='Number of Components')

        with self.frameLayout('Filters', False):
            self.addTextField('filterKeep', label='Filter Keep', annotation='Enter the component IDs to add to the selection. e.g. 1, 5, 6-10')
            self.addTextField('filterRemove', label='Filter Remove', annotation='Enter the component IDs to remove from the selection. e.g. 1, 5, 6-10')
        
        with self.frameLayout('Utilities', False):
           self.addEnum('conversionMode', label='Convert Selection')

        # Hideable controls
        with self.stackedLayout(ref='stacked'):

            with self.page():
                with self.frameLayout('Vertex only', False):
                    self.addEnum('spokeVertexMode', label='Spoke Mode')
                    self.addSlider('spokeVertexCount', label='Spoke Count')
            with self.page():
                with self.frameLayout('Face only', False):
                    self.addEnum('spokeVertexMode', label='Edge Count Mode')
                    self.addSlider('spokeVertexCount', label='Edge Count')

        self.addSpacing(pix(5))
        self.createAttributeListener('componentMode', self.updateControlDimming)
        self.createAttributeListener('enableModulus', self.updateControlDimming)
        self.createAttributeListener('enableComponentSize', self.updateControlDimming)
        self.createAttributeListener('normalAngleMode', self.updateControlDimming)
        self.createAttributeListener('enable', self.enableChanged)
        self.createAttributeListener('componentCounts', self.compCountUpdate)

        self.uuid = 0
        self.nodeChanged()
        self.resetView()
        self.updateControlDimming()
    
    def updateControlDimming(self):
        componentMode = cmds.getAttr(self.name + '.componentMode')
        enableModulus = cmds.getAttr(self.name + '.enableModulus')
        enableCompSize = cmds.getAttr(self.name + '.enableComponentSize')
        normalAngleMode = cmds.getAttr(self.name + '.normalAngleMode')

        if componentMode == 3:
            self.setLayoutHidden('stacked', False)
            self.setIndex('stacked', 0)
        elif componentMode == 1:
            self.setLayoutHidden('stacked', False)
            self.setIndex('stacked', 1)
        else:
            self.setLayoutHidden('stacked', True)

        self.setControlEnabled(self.enableComponentSize, componentMode == 1 or componentMode == 2)

        self.setControlEnabled(self.sizeMode, (componentMode == 1 or componentMode == 2) and enableCompSize)
        self.setControlEnabled(self.faceAreaMin, componentMode == 1 and enableCompSize)
        self.setControlEnabled(self.faceAreaMax, componentMode == 1 and enableCompSize)
        self.setControlEnabled(self.edgeLengthMin, componentMode == 2 and enableCompSize)
        self.setControlEnabled(self.edgeLengthMax, componentMode == 2 and enableCompSize)
        self.setControlEnabled(self.componentSpaceMode, enableCompSize)

        self.setControlEnabled(self.modulus, enableModulus)

        self.setControlEnabled(self.normalAngleMode, componentMode == 1 or componentMode == 3)
        self.setControlEnabled(self.growResultMax, (componentMode == 1 or componentMode == 3) and normalAngleMode != 1)
        self.setControlEnabled(self.growResultMin, (componentMode == 1 or componentMode == 3) and normalAngleMode != 1)
        self.setControlEnabled(self.normalAngle, (componentMode == 1 or componentMode == 3) and normalAngleMode == 2)
        self.setControlEnabled(self.useSmoothEdges, componentMode == 2)

        for i in range(self.dropWidget.listWidget.count()):
            item = self.dropWidget.listWidget.item(i)
            itemWidget = self.dropWidget.listWidget.itemWidget(item)
            itemWidget.proSetUuid = self.dropWidget.uuid
            itemWidget.setIcon()

        self.enableChanged()
        self.compCountUpdate()

    def enableClicked(self):
        self.enableBtn.isOn = not self.enableBtn.isOn
        self.updateEnableBtn()

        cmds.setAttr(self.name + '.enable', self.enableBtn.isOn)

    def updateEnableBtn(self):
        self.enableBtn.setImage('out_MASH_Enable' if self.enableBtn.isOn else 'out_MASH_Disable')

    def enableChanged(self):
        new = cmds.getAttr(self.name + '.enable')
        self.enableBtn.isOn = new
        self.updateEnableBtn()

    def compCountUpdate(self):
        for i in range(self.dropWidget.listWidget.count()):
            item = self.dropWidget.listWidget.item(i)
            itemWidget = self.dropWidget.listWidget.itemWidget(item)
            parentNode = cmds.ls(self.dropWidget.uuid, long=True)[0]            
            componentCount = cmds.getAttr(parentNode+'.componentCounts['+str(itemWidget.index)+']')
            itemWidget.numPoints.setText(str(componentCount))

    def showAllClicked(self):
        if self.dropWidget.listWidget.count():
            cmds.select(clear=True)

        for i in range(self.dropWidget.listWidget.count()):
            item = self.dropWidget.listWidget.item(i)
            itemWidget = self.dropWidget.listWidget.itemWidget(item)
            parentNode = cmds.ls(self.dropWidget.uuid, long=True)[0]
            components = cmds.getAttr(parentNode+'.outputComponents['+str(itemWidget.index)+']')
            history = cmds.listHistory(itemWidget.label.text().split(' ')[-1])

            inputMesh = None

            for node in history:
                if cmds.nodeType(node) == 'mesh':
                    inputMesh = node
                    break

            if inputMesh:
                for comp in components:
                    cmds.select( inputMesh+'.'+comp, add=True )
        
    @fx.undoChunk('Drop node')
    def uiDroppedNode(self, data):
        nodes = [x.strip() for x in data.split('\n')]
        if not nodes: return

        for node in nodes:
            if cmds.nodeType(node) == 'transform' or cmds.nodeType(node) == 'mesh':
                history = cmds.listHistory(node)
                showDialogue = False
                for historyNode in history:
                    if showDialogue:
                        break
                    attrs = cmds.listAttr(historyNode, write=True)
                    for attr in attrs:
                        if 'components' in attr.lower():
                            showDialogue = True

                if showDialogue:
                    wrapper = PromptWrapper(node)
                    wrapper.createHistoryPrompt()
                    if wrapper.reply and wrapper.message != 'Cancel':
                        proSetsAPI.connectNode(self.name, wrapper.reply)
                else:
                    cmds.warning('This item has no history that can be used with a ProSet')

            else:
                proSetsAPI.connectNode(self.name, node)

        self.resetView()

    def uiDroppedFalloffNode(self, data):
        nodes = [x.strip() for x in data.split('\n')]
        if not nodes: return

    def uiReorderNodes(self):
        pass

    def uiDeleteNode(self, node):
        pass

    def uiButtonClicked(self, row, btnName):
        pass

    def uiSelected(self):
        pass

    def resetView(self):
        self.updateNodes()
        self.updateControlDimming()
        self.updateFalloffs()

    def updateNodes(self):
        self.dropWidget.uuid = cmds.ls(self.name, uuid=True)

        nodes = cmds.listConnections(self.name + '.outputComponents')
        self.clearItems()

        if not nodes: return

        count = len(nodes)
        for i, n in enumerate(nodes):
            item = psui.RowItem(self.dropWidget.listWidget)
            rowWidget = psui.RowWidget()
            rowWidget.uuid = cmds.ls(n, uuid=True)[0]
            rowWidget.proSetUuid = cmds.ls(self.name, uuid=True)
            rowWidget.setLabel(n)
            rowWidget.index = i
            rowWidget.item = weakref.ref(item)

            self.dropWidget.listWidget.setItemWidget(item, rowWidget)
            self.dropWidget.callbackManager.addRenameCallback(rowWidget.uuid)
            
            # Also watch for the renaming of the mesh itself
            history = cmds.listHistory(n, future=True)
            for node in history:
                if cmds.nodeType(node) == 'mesh':
                    uuid = cmds.ls(node, uuid=True)[0]
                    self.dropWidget.callbackManager.addRenameCallback(uuid)
                    break


            nodeColor = None
            rowColor = None

            self.addItem(item)

    def updateFalloffs(self):
        self.falloffDropWidget.uuid = cmds.ls(self.name, uuid=True)

        nodes = cmds.listConnections(self.name + '.strengthPP')
        self.falloffDropWidget.listWidget.clear()
        if not nodes: return

        count = len(nodes)
        for i, n in enumerate(nodes):
            item = psui.RowItem(self.falloffDropWidget.listWidget)
            rowWidget = psui.FalloffRowWidget()
            rowWidget.uuid = cmds.ls(n, uuid=True)[0]
            rowWidget.proSetUuid = cmds.ls(self.name, uuid=True)
            rowWidget.setLabel(n)
            rowWidget.index = i
            rowWidget.item = weakref.ref(item)

            self.falloffDropWidget.listWidget.setItemWidget(item, rowWidget)
            self.falloffDropWidget.callbackManager.addRenameCallback(rowWidget.uuid)

            self.falloffDropWidget.listWidget.addItem(item)

    def nodeChanged(self):
        resetView = False
        if self.uuid != cmds.ls(self.name, uuid=True):
            self.uuid = cmds.ls(self.name, uuid=True)
            resetView = True

        nodes = cmds.listConnections(self.name + '.outputComponents') or []

        if len(nodes) != self.itemCount():
            resetView = True

        if resetView:
            self.resetView()

# Utilities
    def repaintList(self):
        self.dropWidget.listWidget.viewport().repaint()

    def itemAt(self, index):
        return self.dropWidget.listWidget.item(index)

    def itemCount(self):
        return self.dropWidget.listWidget.count()

    def clearItems(self):
        self.dropWidget.listWidget.clear()

    def addItem(self, item):
        self.dropWidget.listWidget.addItem(item)

    def draggedNode(self):
        return self.dropWidget.listWidget.drag_node
        
    def dragStartIndex(self):
        return self.dropWidget.listWidget.drag_row