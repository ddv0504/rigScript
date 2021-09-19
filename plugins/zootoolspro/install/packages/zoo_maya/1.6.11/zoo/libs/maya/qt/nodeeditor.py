from maya import cmds
from zoo.libs.maya.qt import mayaui
from zoo.libs.maya.api import nodes as apiNodes
from zoovendor.Qt import QtWidgets, QtCore


def getPrimaryNodeEditor():
    """Find and return the name of the primary node editor if it exists.

    :return: The node editor name
    :rtype: str
    """
    allNEs = cmds.getPanel(scriptType="nodeEditorPanel")
    for oneNE in allNEs:
        ned = oneNE + "NodeEditorEd"
        if cmds.nodeEditor(ned, query=True, primary=True):
            return ned
    return ""


def createNodeEditor():
    """Creates(opens) the maya node editor.

    :return: Returns the NodeEditorWrapper object linked to the current node editor.
    :rtype: :class:`NodeEditorWrapper`
    """
    cmds.NodeEditorWindow()
    return NodeEditorWrapper()


class NodeEditorWrapper(QtCore.QObject):
    @staticmethod
    def nodeEditorAsQtWidgets(nodeEditor):
        nodeEdPane = mayaui.toQtObject(nodeEditor)
        view = nodeEdPane.findChild(QtWidgets.QGraphicsView)
        return nodeEdPane, view, view.scene()

    @staticmethod
    def itemsRect(items):
        sourceRect = QtCore.QRect()

        for item in items:
            sourceRect = sourceRect.united(QtCore.QRect(*item.sceneBoundingRect().getRect()))
        return sourceRect

    def __init__(self, nodeEditor=None):
        super(NodeEditorWrapper, self).__init__()
        if not nodeEditor:
            self.mayaName = getPrimaryNodeEditor()
            self.setObjectName(self.mayaName)
            if not self.mayaName:
                self.editor, self.view, self.scene = None, None, None
            else:
                self.editor, self.view, self.scene = NodeEditorWrapper.nodeEditorAsQtWidgets(getPrimaryNodeEditor())
        else:
            self.editor, self.view, self.scene = NodeEditorWrapper.nodeEditorAsQtWidgets(nodeEditor)

    def exists(self):
        objName = self.objectName()
        if objName:
            return cmds.nodeEditor(objName, exists=True)
        return False

    def show(self):
        cmds.NodeEditorWindow()
        self.editor, self.view, self.scene = NodeEditorWrapper.nodeEditorAsQtWidgets(getPrimaryNodeEditor())

    def selectedNodeItems(self):
        # check against type instead of isinstance since graphicsPathItem inherents from QGraphicsItem
        return [i for i in self.scene.selectedItems() if type(i) == QtWidgets.QGraphicsItem]

    def selectedConnections(self):
        return [i for i in self.scene.selectedItems() if type(i) == QtWidgets.QGraphicsPathItem]

    def addNodes(self, nodes):
        """Adds a list of nodes to the current node editor

        :param nodes: a list of maya mobject representing valid nodes
        :type nodes: list(:class:`om2.MObject`)
        """

        for n in nodes:
            cmds.nodeEditor(self.objectName(), addNode=apiNodes.nameFromMObject(n))

    def graphDownstreamFromSelection(self):
        """This Graphs the downstream nodes from the currently selected nodes.
        """
        cmds.nodeEditor(self.mayaName, edit=True, rootsFromSelection=True, downstream=True)

    def alignLeft(self, items=None):
        items = items or self.selectedNodeItems()
        xPos = min([i.pos().x() for i in items])
        for item in items:
            item.setX(xPos)

    def alignRight(self, items):
        items = items or self.selectedNodeItems()
        xPos = max([i.pos().x() for i in items])
        for item in items:
            item.setX(xPos)

    def alignTop(self, items):
        items = items or self.selectedNodeItems()
        xPos = min([i.pos().y() for i in items])
        for item in items:
            item.setY(xPos)

    def alignBottom(self, items):
        items = items or self.selectedNodeItems()
        xPos = max([i.pos().y() for i in items])
        for item in items:
            item.setY(xPos)

    def alignCenterX(self, items):
        items = items or self.selectedNodeItems()
        rect = NodeEditorWrapper.itemsRect(items)
        center = rect.center()
        for i in items:
            i.setX(center.x())

    def alignCenterY(self, items):
        items = items or self.selectedNodeItems()
        rect = NodeEditorWrapper.itemsRect(items)
        center = rect.center()
        for i in items:
            i.setY(center.y())
