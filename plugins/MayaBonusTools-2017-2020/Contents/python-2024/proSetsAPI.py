### See the file "LICENSE.txt" for the full license governing this code.
import maya.cmds as cmds
from openMASH import mashGetMObjectFromNameOne
import maya.OpenMaya as om
import ast
try:
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication
except:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

'''
Example usage:

import proSetsAPI

proSetsAPI.resetInputComponents('deleteComponent1','deleteComponents')
proSetsAPI.setInputComponents('deleteComponent1','deleteComponents')
'''


def setInputComponents(nodeName, channelName):
    selectedFaces = cmds.filterExpand( ex=True, sm=34 ) or []
    selectedVertices = cmds.filterExpand( ex=True, sm=31 ) or []
    selectedEdges = cmds.filterExpand( ex=True, sm=32 ) or []

    selectedComponents = []
    buttons = []
    if selectedFaces:
        selectedComponents = selectedFaces
        buttons.append('Faces')
    if selectedVertices:
        selectedComponents = selectedVertices
        buttons.append('Vertices')
    if selectedEdges:
        selectedComponents = selectedEdges
        buttons.append('Edges')

    if len(buttons) > 1:
        buttons.append('Cancel')
        message = 'More than one component type detected, please specify one:'
        returnStr = cmds.confirmDialog( title='Select Component Type', message=message, button=buttons, defaultButton=buttons[0], cancelButton='Cancel', dismissString='Cancel' )
        print (returnStr)
        if returnStr == 'Faces':
            selectedComponents = selectedFaces
        elif returnStr == 'Vertices':
            selectedComponents = selectedVertices
        elif returnStr == 'Edges':
            selectedComponents = selectedEdges

    if len(selectedComponents) == 0:
        return

    commandString = 'cmds.setAttr("'+nodeName+'.'+channelName+'",'+str(len(selectedComponents))+","

    for component in selectedComponents:
        commandString += "'"+component.split('.')[-1]+"',"
        
    commandString += " type='componentList')"

    ast.literal_eval(commandString)


def resetInputComponents(node, channelName):
    cmds.setAttr(node+'.'+channelName,0,type='componentList')

def connectNode(proSet, externalNode, componentAttribute=None):
    ###
    ### First connect the ProSet to the tool
    ###
    connId = str(nextFreeUnconnectedMulti(proSet, "inputData"))

    if cmds.objExists(externalNode+'.inputComponents'):
        cmds.connectAttr(proSet+'.outputComponents['+connId+']', externalNode+'.inputComponents')
    elif componentAttribute:
        # a custom component attribute can be specified by a user if so desired
        cmds.connectAttr(proSet+'.outputComponents['+connId+']', externalNode+'.'+componentAttribute)
    else:
        # No default attribute found, so look for any attribute with 'components' in the name.
        # We should also check for type
        attrs = cmds.listAttr(externalNode, write=True)
        for attr in attrs:
            if 'components' in attr.lower():
                cmds.connectAttr(proSet+'.outputComponents['+connId+']', externalNode+'.'+attr)
                break

    ###
    ### Now connect the mesh to the ProSet (simply to trick a dirty which keeps us up to date)
    ###
    inId = str(nextFreeUnconnectedMulti(proSet, "inputData"))
    toolAttrs = cmds.listAttr(externalNode, write=True)
    # Known attribute names for meshes
    meshAttrs = ['inputPolymesh', 'inputGeometry', 'inputMesh', 'inMesh', 'inWorldMesh']
    foundAttrs = set(toolAttrs).intersection(set(meshAttrs))
    if foundAttrs:
        attrToUse = next(iter(foundAttrs))
        inMeshConns = cmds.listConnections(externalNode+'.'+attrToUse, plugs=True)
        inMeshConnsNode = cmds.listConnections(externalNode+'.'+attrToUse)
        if inMeshConns:
            cmds.connectAttr(inMeshConns[0], proSet+'.inputData['+connId+'].inMesh')

            history = cmds.listHistory(externalNode)
            print (history)
            for node in history:
                if cmds.nodeType(node) == 'mesh':
                    parent = cmds.listRelatives(node, p=True, pa=True)
                    if parent:
                        cmds.connectAttr(parent[0]+'.worldMatrix[0]', proSet+'.inputData['+connId+'].inWorldMatrix')
                        break


def disconnectNode(proSet, connId):
    connId = str(connId)
    matrixConn = cmds.listConnections(proSet+'.inputData['+connId+'].inWorldMatrix', plugs=True)
    meshConn = cmds.listConnections(proSet+'.inputData['+connId+'].inMesh', plugs=True)
    outConn = cmds.listConnections(proSet+'.outputComponents['+connId+']', plugs=True)

    if matrixConn:
        cmds.disconnectAttr(matrixConn[0], proSet+'.inputData['+connId+'].inWorldMatrix')

    if meshConn:
        cmds.disconnectAttr(meshConn[0], proSet+'.inputData['+connId+'].inMesh')

    if outConn:
        cmds.disconnectAttr(proSet+'.outputComponents['+connId+']', outConn[0])

    # Maya will crash with existing connections reguardless of the break flag.
    cmds.removeMultiInstance(proSet+'.inputData['+connId+']', b=True )

    resetInputComponents(proSet, 'inputData['+connId+'].inputComponents')

def deleteNode(proSet, connId):
    connId = str(connId)
    outConn = cmds.listConnections(proSet+'.outputComponents['+connId+']', plugs=False)

    disconnectNode(proSet, connId)

    if outConn:
        cmds.delete(outConn[0])

def createProSet():
    selected = cmds.ls(sl=True)
    newSet = cmds.createNode('proSet')

    # Prevent Maya tripping over itself (and crashing)
    cmds.flushIdleQueue()

    import maya.app.flux.imports as imports
    import maya.app.flux.core as fx
    modifiers = QApplication.keyboardModifiers()
    if modifiers == Qt.AltModifier and selected:
        import AEproSetTemplate as aet
        for node in selected:
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
                    wrapper = aet.PromptWrapper(node)
                    wrapper.createHistoryPrompt()
                    if wrapper.reply and wrapper.message != 'Cancel':
                        connectNode(newSet, wrapper.reply)

def nextFreeUnconnectedMulti(nodeName, attributeName):
    thisNode = mashGetMObjectFromNameOne(nodeName)
    fnNode = om.MFnDependencyNode(thisNode)
    attribute = fnNode.attribute(attributeName)
    inPlug = om.MPlug( thisNode, attribute )
    count = inPlug.numConnectedElements()
    existingArray = om.MIntArray()
    inPlug.getExistingArrayAttributeIndices(existingArray)

    if existingArray:
        start = 0
        limit = len(existingArray)
        start = start if start is not None else existingArray[0]
        limit = limit if limit is not None else existingArray[-1]
        for i in range(start,limit + 1):
            if i not in existingArray:
                return i
            else:
                plug = inPlug.elementByPhysicalIndex(i)
                if not plug.numConnectedChildren():
                    return i
                    
    else:
        return 0

def nextFreeMulti(nodeName, attributeName):
    thisNode = mashGetMObjectFromNameOne(nodeName)
    fnNode = om.MFnDependencyNode(thisNode)
    attribute = fnNode.attribute(attributeName)
    inPlug = om.MPlug( thisNode, attribute )
    count = inPlug.numConnectedElements()
    existingArray = om.MIntArray()
    inPlug.getExistingArrayAttributeIndices(existingArray)

    if existingArray:
        start = 0
        limit = len(existingArray)
        start = start if start is not None else existingArray[0]
        limit = limit if limit is not None else existingArray[-1]
        return [i for i in range(start,limit + 1) if i not in existingArray][0]
    else:
        return 0

    return freeIndex