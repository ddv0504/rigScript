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

def bt_flattenComponents():
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    import bt_flattenComponentsUtils as utils

    componentList = cmds.filterExpand(ex=1, sm=(31,32,34))
    cmds.select( cmds.polyListComponentConversion(componentList, tv=True), r=1)
    vertList = cmds.filterExpand(ex=1,sm=31)
    vertsObjectName = vertList[0].split('.')[0]

    type = cmds.nodeType(vertsObjectName)
    vertsObject = cmds.listRelatives(vertsObjectName,p=1) if type == 'mesh' else vertsObjectName

    # Calculate avg position and normals for selected verts
    cmds.select(vertList)
    avgNormal   = utils.getAvgVertNormal()
    avgPosition = utils.getAvgVertPosition()

    # Create snapping plane
    snapPlane = cmds.polyPlane(sx=1,sy=1)[0]
    snapPlaneParent = cmds.group(name="snapPlane")
    node = om.MFnTransform(utils.nameToNode(snapPlaneParent))
    node.setTranslation(om.MVector(avgPosition), om.MSpace.kObject)
    node.setScale((10,10,10))

    # Break shader connection
    shapes = cmds.listRelatives(snapPlane, shapes = True)
    utils.disconnectAttribute(cmds.listConnections(shapes, plugs = 1)[0])

    #create temporary locator for origenting plane
    orientLocatorName = cmds.spaceLocator()[0]
    orientLocatorNode = om.MFnTransform(utils.nameToNode(orientLocatorName))
    orientLocatorNode.setTranslation(om.MVector(avgPosition), om.MSpace.kObject)
    cmds.delete(cmds.orientConstraint(vertsObject, orientLocatorName, offset=(0,0,0)))

    cmds.move(avgNormal[0], avgNormal[1], avgNormal[2], orientLocatorName, r=1, os=1)

    #temporay orientation contraint
    cmds.delete(cmds.aimConstraint(orientLocatorName, snapPlaneParent, aimVector=[0,1,0]), orientLocatorName)

    #snap verts to plane
    cmds.select(snapPlane,vertList, r=1)
    cmds.transferAttributes(pos=1,nml=0,uvs=0,col=0)

    cmds.setAttr('{}.displayHandle'.format(snapPlaneParent), 1)
    cmds.setAttr('{}.displayLocalAxis'.format(snapPlaneParent), 1)
    cmds.setAttr('{}.overrideEnabled'.format(snapPlane), 1)
    cmds.setAttr('{}.overrideDisplayType'.format(snapPlane), 2)

    cmds.select(snapPlaneParent, r=1)
    msg = 'Components flattened.  Use manipulator to interactively change distance and orientation.  Scale can be used to expand snap area'
    cmds.headsUpMessage(msg,t=4)


