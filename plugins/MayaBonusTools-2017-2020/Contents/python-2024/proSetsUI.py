### See the file "LICENSE.txt" for the full license governing this code.
from maya.app.flux.imports import *
import maya.app.flux.core as fx
from maya.app.flux.core import pix

import proSetsAPI as psapi
from openMASH import mashGetMObjectFromNameTwo

from copy import deepcopy

'''
This is a generic QListWidget subclass for use with DropListWidget
Subclass this to create your own List Widget behaviour.
'''
class XListWidget(qt.QListWidget):
    def __init__(self):
        qt.QListWidget.__init__(self)

        self.dataDelegate = None
        self.pixmap = fx.getPixmap('DragDrop')
        self.iconLabel = qt.QLabel(self)
        self.iconLabel.setPixmap(self.pixmap)
        self.iconLabel.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.iconWidth = pix(24)

    def setDataDelegate(self, dataDelegate):
        self.dataDelegate = dataDelegate

    def resizeEvent(self, e):
        qt.QListWidget.resizeEvent(self, e)
        pos = self.contentsRect().center()
        pos.setX(pos.x() - self.pixmap.size().width()/(2 * self.pixmap.devicePixelRatio()))
        pos.setY(pos.y() - self.pixmap.size().height()/(2 * self.pixmap.devicePixelRatio()))
        self.iconLabel.move(pos)

    def paintEvent(self, e):
        if not self.count() and self.iconLabel.isHidden():
            self.iconLabel.show()
        elif self.count() and not self.iconLabel.isHidden():
            self.iconLabel.hide()

        qt.QListWidget.paintEvent(self,e)   

    def mousePressEvent(self, event):
        self.clearSelection()
        qt.QListWidget.mousePressEvent(self, event) 

class FalloffListWidget(XListWidget):
    def __init__(self):
        XListWidget.__init__(self)
        self.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.setSelectionMode(qt.QAbstractItemView.SingleSelection)
        self.customContextMenuRequested.connect(self.openTreeMenu)
        self.itemDoubleClicked.connect(self.doubleClick)

    def openTreeMenu(self, position):
        treeMenu = qt.QMenu(self)
        if len(self.selectedItems()):
            treeMenu.addAction(fx.getIconFromName('Delete'), 'Delete', self.deleteFalloffNode)
        else:
            treeMenu.addAction(fx.getIconFromName('out_MASH_CreateUtility'), 'Add', self.createFalloffNode)

        treeMenu.exec_(self.mapToGlobal(position))

    def createFalloffNode(self):
        parentNode = cmds.ls(self.dataDelegate.uuid, long=True)[0]
        newFalloff = cmds.createNode('MASH_Falloff', n=parentNode+'FalloffShape')
        nextFree = psapi.nextFreeMulti(parentNode, 'strengthPP')
        cmds.connectAttr(newFalloff+'.falloffOut', parentNode+'.strengthPP['+str(nextFree)+']')
        cmds.setAttr(newFalloff+'.innerRadius', 1.0)
        cmds.setAttr(newFalloff+'.invertFalloff', l=True)
        cmds.setAttr(newFalloff+'.falloffEventType', l=True)
        cmds.setAttr(newFalloff+'.componentReadType', l=True)
        cmds.setAttr(newFalloff+'.vertexColour', l=True)
        self.dataDelegate.updateView.emit()

    def deleteFalloffNode(self):
        parentNode = cmds.ls(self.dataDelegate.uuid, long=True)[0]
        itemWidget = self.itemWidget(self.currentItem())
        connId = str(self.currentRow())
        falloffConn = cmds.listConnections(parentNode+'.strengthPP['+connId+']', plugs=True)
        if falloffConn:
            cmds.disconnectAttr(falloffConn[0], parentNode+'.strengthPP['+connId+']')

        cmds.delete(itemWidget.label.text())
        
        self.dataDelegate.updateView.emit()

    def doubleClick(self, index):
        widget = self.itemWidget(self.currentItem())
        nodeName = widget.label.text()
        cmds.select(nodeName)

class CustomListWidget(XListWidget):
    def __init__(self):
        XListWidget.__init__(self)
        self.objectName = "ProSetListWidget"
        self.dataDelegate = None
        self.itemDoubleClicked.connect(self.doubleClick)
        self.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openTreeMenu)
        self.setSelectionMode(qt.QAbstractItemView.SingleSelection)

    def setDataDelegate(self, dataDelegate):
        self.dataDelegate = dataDelegate

    def openTreeMenu(self, position):
        if len(self.selectedItems()):
            treeMenu = qt.QMenu(self)
            self.setupTreeMenu(treeMenu, position)
            treeMenu.exec_(self.mapToGlobal(position))

    def setupTreeMenu(self, treeMenu, position):
        treeMenu.addAction(fx.getIconFromName('ProSet_BreakConnection'), 'Disconnect', self.disconnectNode)
        treeMenu.addAction(fx.getIconFromName('Delete'), 'Delete', self.deleteNode)

        selMenu = treeMenu.addMenu(fx.getIconFromName('ProSet_Set'),'User Selection')

        selMenu.addAction(fx.getIconFromName('ProSet_Set'), 'Set', self.setUserSelection)
        selMenu.addAction(fx.getIconFromName('ProSet_Show'), 'Show', self.showUserSelection)
        selMenu.addAction(fx.getIconFromName('ProSet_Clear'), 'Clear', self.clearUserSelection)

    def showUserSelection(self):
        if self.currentItem():
            self.itemWidget(self.currentItem()).show()

    def setUserSelection(self):
        if self.currentItem():
            self.itemWidget(self.currentItem()).set()

    def clearUserSelection(self):
        if self.currentItem():
            self.itemWidget(self.currentItem()).clear()

    @fx.undoChunk('Disconnect node')
    def disconnectNode(self):
        if self.currentItem() and self.dataDelegate:
            parentNode = cmds.ls(self.dataDelegate.uuid, long=True)[0]
            psapi.disconnectNode(parentNode ,self.currentRow())
            self.dataDelegate.updateView.emit()

    @fx.undoChunk('Delete node')
    def deleteNode(self):
        if self.currentItem() and self.dataDelegate:
            parentNode = cmds.ls(self.dataDelegate.uuid, long=True)[0]
            psapi.deleteNode(parentNode ,self.currentRow())
            self.dataDelegate.updateView.emit()

    def doubleClick(self, index):
        widget = self.itemWidget(self.currentItem())
        modellingTool = widget.label.text().split(' ')[-1]
        cmds.select(modellingTool)


class XRowWidget(qt.QWidget):
    def __init__(self):
        qt.QWidget.__init__(self)
        self.setFixedHeight(pix(28))
        self.setLayout(qt.QHBoxLayout())
        self.layout().setContentsMargins(pix(10),0,pix(5),0)
        self.layout().addSpacing(pix(2))

        self.uuid = None
        self.proSetUuid = None
        self.item = None
        self.index = None

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        painter.setRenderHint(qt.QPainter.Antialiasing, True)
        painter.setPen(qt.QColor(0, 0, 0, 0))
        painter.setBrush(qt.QColor(217,148,86))

        painter.drawRect(0,0, 5, self.height())

        qt.QWidget.paintEvent(self, event) 

class FalloffRowWidget(XRowWidget):
    def __init__(self):
        XRowWidget.__init__(self)

        self.icon = qt.QLabel()
        self.icon.setPixmap(fx.getPixmap('out_MASH_Falloff'))
        self.layout().addWidget(self.icon)

        self.label = qt.QLabel()
        self.layout().addWidget(self.label)

        self.layout().addStretch()

    def setLabel(self, text):
        self.label.setText(text)

class RowWidget(XRowWidget):
    def __init__(self):
        XRowWidget.__init__(self)
        
        self.meshIcon = qt.QLabel()
        self.meshIcon.setPixmap(fx.getPixmap('out_mesh'))
        self.layout().addWidget(self.meshIcon)

        self.label = qt.QLabel()
        self.layout().addWidget(self.label)

        self.layout().addStretch()
        self.showOnClickedBtn = fx.ImageButton('ProSet_ShowSet', highlighted=False)
        self.showOnClickedBtn.clicked.connect(self.showOnClickClicked)
        self.showOnClickedBtn.setToolTip('Show the selected components in the viewport. Alt + click to go to the shape.')
        self.layout().addWidget(self.showOnClickedBtn)
        self.layout().addSpacing(pix(3))

        self.numPoints = qt.QLabel('0')
        self.numPoints.setStyleSheet('QLabel{border:0px; border-radius:%dpx; background-color: rgba(43,43,43)}' % pix(2))
        self.numPoints.setContentsMargins(pix(20),pix(2),pix(2),pix(2))
        self.numPoints.setFixedHeight(pix(18))
        self.numPoints.setFixedWidth(pix(80))

        self.pointIcon = qt.QLabel(parent=self.numPoints)
        self.pointIcon.move(pix(1),pix(1))

        self.layout().addSpacing(2)
        self.layout().addWidget(self.numPoints, 0)

    def showEvent(self, event):
        self.repaint()
        self.showOnClickedBtn.repaint()
        self.showOnClickedBtn.update()
        self.showOnClickedBtn.redrawPixmap()

    def showOnClickClicked(self):
        parentNode = cmds.ls(self.proSetUuid, long=True)[0]
        cmds.select(clear=True)
        components = cmds.getAttr(parentNode+'.outputComponents['+str(self.index)+']')
        meshNode = self.label.text().split(' ')[0]
        history = cmds.listHistory(self.label.text().split(' ')[-1])
        history.append(meshNode)
        inputMesh = None
        for node in history:
            if cmds.nodeType(node) == 'mesh':
                inputMesh = node
                break

        if inputMesh:
            for comp in components:
                cmds.select( inputMesh+'.'+comp, add=True )

        modifiers = qt.QApplication.keyboardModifiers()
        if modifiers != QtCore.Qt.AltModifier:
            cmds.select(parentNode, add=True, noExpand=True)

    def setLabel(self, text):
        history = cmds.listHistory(text, future=True)
        inputMesh = None

        for node in history:
            if cmds.nodeType(node) == 'mesh':
                inputMesh = node
                break

        if inputMesh:
            label = inputMesh+" -> "+text
            self.label.setText(label)
        else:
            self.label.setText(text)

        self.setIcon()

    def setIcon(self):
        parentNode = cmds.ls(self.proSetUuid, long=True)[0]
        componentMode =  cmds.getAttr(parentNode+'.componentMode')
        iconName = 'ProSet_Count_Poly'
        if componentMode == 2:
            iconName = 'ProSet_Count_Edge'
        elif componentMode == 3:
            iconName = 'ProSet_Count_Vert'

        pixmap = fx.scalePixmap(fx.getPixmap(iconName), 16, 16)
        self.pointIcon.setPixmap(pixmap)

    @fx.undoChunk('Show Input Components')
    def show(self, clear = True):
        parentNode = cmds.ls(self.proSetUuid, long=True)[0]
        components = cmds.getAttr(parentNode+'.inputData['+str(self.index)+'].inputComponents')
        if components:
            history = cmds.listHistory(self.label.text().split(' ')[-1])
            inputMesh = None

            for node in history:
                if cmds.nodeType(node) == 'mesh':
                    inputMesh = node
                    break

            if inputMesh:
                if clear: cmds.select(clear=True)
                for comp in components:
                    cmds.select( inputMesh+'.'+comp, add=True )

    @fx.undoChunk('Set Input Components')
    def set(self):
        parentNode = cmds.ls(self.proSetUuid, long=True)[0]
        selectedFaces = cmds.filterExpand( ex=True, sm=34 ) or []
        selectedVertices = cmds.filterExpand( ex=True, sm=31 ) or []
        selectedEdges = cmds.filterExpand( ex=True, sm=32 ) or []
        componentMode = cmds.getAttr(parentNode+'.componentMode')
        if (componentMode == 1 and len(selectedFaces)) or (componentMode == 2 and len(selectedEdges)) or (componentMode == 3 and len(selectedVertices)):
            psapi.setInputComponents(parentNode,'inputData['+str(self.index)+'].inputComponents')
        else:
            cmds.warning("No valid components selected")

    @fx.undoChunk('Clear Input Components')
    def clear(self):
        parentNode = cmds.ls(self.proSetUuid, long=True)[0]
        cmds.setAttr(parentNode+'.inputData['+str(self.index)+'].inputComponents',0 , type='componentList')

class RowItem(qt.QListWidgetItem):
    def __init__(self, parent, index=None):
        qt.QListWidgetItem.__init__(self, parent)
        self.setSizeHint(qt.QSize(self.sizeHint().width(), pix(28)))
        self.setBackground(parent.palette().color(qt.QPalette.Button))


class DropListWidget(qt.QWidget):
    dropped = qt.Signal(str)
    reorder = qt.Signal()
    updateView = qt.Signal()
    buttonClicked = qt.Signal(int, str)
    selected = qt.Signal()

    def __init__(self, listWidget, uuid, title, rollOverMessage = None):
        qt.QWidget.__init__(self)
        fx.setVLayout(self)
        #
        #   SELF
        #
        self.setAcceptDrops(True)
        self.layout().setContentsMargins(pix(5),pix(5),pix(11),pix(5))
        self.layout().setSpacing(pix(5))
        self.uuid = None

        #
        #   CALLBACK MANAGER
        #
        self.callbackManager = CallbacksManager()
        self.callbackManager.objRenamed = self.objRenamed

        #
        #   HEADER
        #
        self.rollOverMessage = rollOverMessage
        self.title = title
        self.headerLayout = qt.QHBoxLayout()
        self.headerTitle = qt.QLabel(title)
        self.headerTitle.setContentsMargins(pix(2),pix(0),pix(0),pix(0))
        self.headerLayout.addWidget(self.headerTitle)
        self.layout().addLayout(self.headerLayout)

        #
        #   LIST WIDGET
        #
        self.listWidget = listWidget
        self.listWidget.setDataDelegate(self)
        self.listWidget.setFocusPolicy(qt.Qt.NoFocus)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSpacing(1)
        self.listWidget.setDefaultDropAction(qt.Qt.MoveAction)
        self.listWidget.setDropIndicatorShown(True)
        self.listWidget.showDropIndicator = True
        self.listWidget.setAcceptDrops(True)
        self.listWidget.setFixedHeight(pix(150))
        self.layout().addWidget(self.listWidget)

    def enterEvent(self,event):
        if self.rollOverMessage:
            self.headerTitle.setText(self.rollOverMessage)

    def leaveEvent(self,event):
        self.headerTitle.setText(self.title)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()

    def dropEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            self.dropped.emit(e.mimeData().text())
        else:
            self.reorder.emit()

    def selectionChanged(self):
        self.selected.emit()

    def buttonPressed(self, index, buttonName):
        self.buttonClicked.emit(index.row(), buttonName)

    def objRenamed(self, node, oldName, clientData):
        uuid = nom.MFnDependencyNode(node).uuid().asString()
        self.manageRename(uuid)

    def manageRename(self, uuid):
        self.updateView.emit()
        self.callbackManager.renameNode(uuid)

class CallbacksManager(qt.QObject):
    objRenamed = None
    manageRename = None
    renameCallbacks = {}

    def addRenameCallback(self, uuid):
        name = cmds.ls(uuid, long=True)[0]
        node = mashGetMObjectFromNameTwo(name)
        self.renameCallbacks[uuid] = nom.MNodeMessage.addNameChangedCallback(node, self.objRenamed, name)

    def removeRenameCallback(self, uuid):
        if uuid in self.renameCallbacks:
            nom.MNodeMessage.removeCallback(self.renameCallbacks[uuid])
            del self.renameCallbacks[uuid]

    def renameNode(self, uuid):
        self.removeRenameCallback(uuid)
        self.addRenameCallback(uuid)