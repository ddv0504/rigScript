# Copyright (C) 1997-2020 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.
#
# Original Author: Steven T. L. Roselle
# Last Updated: 2020/10/06
#
from builtins import range

def bt_flattenComponentsManip():
    import maya.cmds as cmds
    import bt_flattenComponentsUtils as utils

    componentList = cmds.filterExpand(ex=1, sm=(31,32,34))
    cmds.select( cmds.polyListComponentConversion(componentList, tv=True), r=1)
    vertList = cmds.filterExpand(ex=1,sm=31)

    vertsObjectName = cmds.ls(vertList[0], o=True)

    if cmds.nodeType(vertsObjectName) == 'mesh':
        vertsObject = cmds.listRelatives(vertsObjectName,p=1)
    else:
        vertsObject = vertsObjectName

    # Calculate avg position and normals for selected verts
    cmds.select(vertList)
    avgNormal   = utils.getAvgVertNormal()
    avgPosition = utils.getAvgVertPosition()

    # Create snapping plane
    snapPlane = cmds.polyPlane(sx=1,sy=1)[0]
    snapPlaneParent = cmds.group(name="snapPlane")
    attr = '{}.translate'.format(snapPlaneParent)
    for i, axis in enumerate(['X', 'Y', 'Z']):
        cmds.setAttr('{}{}'.format(attr,axis), avgPosition[i])

    # Account for larger objects
    attr = '{}.scale'.format(snapPlane)
    for axis in ['X', 'Y', 'Z']:
        cmds.setAttr('{}{}'.format(attr,axis), 10000)

    # Break shader connection
    shapes = cmds.listRelatives(snapPlane, shapes=True)
    utils.disconnectAttribute(cmds.listConnections(shapes, plugs = 1)[0])

    # Create temporary locator for orienting plane
    orientLocator = cmds.spaceLocator()
    attr = '{}.translate'.format(orientLocator[0])
    for i, axis in enumerate(['X', 'Y', 'Z']):
        cmds.setAttr('{}{}'.format(attr,axis), avgPosition[i])

    oc = cmds.orientConstraint(vertsObject, orientLocator, offset=(0,0,0))
    cmds.delete(oc)

    cmds.move(avgNormal[0], avgNormal[1], avgNormal[2], orientLocator, r=1, os=1)

    # Temporay orientation contraint
    ac = cmds.aimConstraint(orientLocator, snapPlaneParent, aimVector=[0,1,0])
    cmds.delete(ac, orientLocator)

    # Snap verts to plane
    cmds.select(snapPlane,vertList, r=1)

    cmds.transferAttributes(pos=1,nml=0,uvs=0,col=0)

    cmds.setAttr('{}.displayHandle'.format(snapPlaneParent), 1)
    cmds.setAttr('{}.displayLocalAxis'.format(snapPlaneParent), 1)
    cmds.setAttr('{}.overrideEnabled'.format(snapPlane), 1)
    cmds.setAttr('{}.overrideDisplayType'.format(snapPlane), 2)
    cmds.setAttr('{}.visibility'.format(snapPlane), 0)

    #cmds.delete(snapPlaneParent)
    #print('Components flattened')

    cmds.select(snapPlaneParent, r=1)
    cmds.setToolTo('moveSuperContext')
    

