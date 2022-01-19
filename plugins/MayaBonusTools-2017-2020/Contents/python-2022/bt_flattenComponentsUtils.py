from builtins import range

import maya.cmds as cmds
import maya.api.OpenMaya as om

def getAvgVertPosition():
    vertList = cmds.filterExpand(ex=1,sm=31)
    cmds.select(vertList,r=1)
    verts = cmds.ls(sl=1,fl=1)

    totalPos = om.MPoint(0.,0.,0.)
    for vert in verts:
        totalPos += om.MPoint(cmds.pointPosition(vert, world=True))

    cmds.select(vertList,r=1)

    count = len(verts)
    if (count == 0):
        print('No verts selected')
        return totalPos

    return list(totalPos/float(count))[0:3]

def getAvgVertNormal():
    def getVertexNormal(vert):
        normals = cmds.polyNormalPerVertex(vert, q=True, normalXYZ=True)
        m = len(normals)//3
        vertn = om.MVector(0.,0.,0.)
        for i in range(m):
            chunk = normals[3*i:3*i+3]
            vertn += om.MVector(chunk[0], chunk[1], chunk[2])
        return vertn/float(m)

    vertList = cmds.filterExpand(ex=1,sm=31)
    cmds.select(vertList,r=1)
    verts = cmds.ls(sl=1,fl=1)

    totalNormal = om.MVector(0.,0.,0.)
    for vert in verts:
        totalNormal += getVertexNormal(vert)

    cmds.select(vertList,r=1)
    count = len(verts)
    if (count == 0):
        print('No verts selected')
        return totalNormal

    totalNormal /= float(count)
    return list(totalNormal.normalize())

def nameToNode(name):
    # Given a node name, return the corresponding MObject
    selectionList = om.MSelectionList()
    selectionList.add(name)
    return selectionList.getDependNode(0)

def disconnectAttribute(attr):
    '''
    https://github.com/LumaPictures/pymel/blob/master/pymel/core/general.py
    Disconnect the attribute in a pymel way
    '''
    source = attr
    disconnectionDirs = ['inputs', 'outputs']
    for disconnectDir in disconnectionDirs:
        disconnectingInputs = (disconnectDir == 'inputs')
        connections = cmds.listConnections(source,source=disconnectingInputs,destination=(not disconnectingInputs),connections=True,plugs=True)
        if connections is None:
            continue
        if disconnectingInputs:
            connections.reverse()
        for i in range(0, len(connections), 2):
            cmds.disconnectAttr(connections[i], connections[i+1])