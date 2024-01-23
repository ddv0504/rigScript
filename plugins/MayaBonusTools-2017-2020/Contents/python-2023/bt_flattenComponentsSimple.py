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
# Last Update: 2020/10/07
#

def bt_flattenComponentsSimple():
    import maya.cmds as cmds
    import bt_flattenComponentsUtils as utils

    componentList = cmds.filterExpand(ex=1, sm=(31,32,34))
    cmds.select( cmds.polyListComponentConversion(componentList, tv=True), r=1)
    vertList = cmds.filterExpand(ex=1,sm=31)

    vertsShapeNode = cmds.ls(vertList[0], o=True)
    vertObject = vertList[0].split('.')[0]

    if(cmds.nodeType(vertsShapeNode) == 'mesh'):
        vertsObject = cmds.listRelatives(vertsShapeNode,p=1)
    else:
        vertsObject = vertsShapeNode

    # calculate avg position and normals for selected verts
    cmds.select(vertList)
    avgNormal   = utils.getAvgVertNormal()
    avgPosition = utils.getAvgVertPosition()

    # create snapping plane
    snapPlane = cmds.polyPlane(sx=1,sy=1)[0]
    cmds.setAttr('{}.visibility'.format(snapPlane), 0)
    snapPlaneParent = cmds.group(name="snapPlane")
    attr = '{}.translate'.format(snapPlaneParent)
    for i, axis in enumerate(['X', 'Y', 'Z']):
        cmds.setAttr('{}{}'.format(attr,axis), avgPosition[i])

    # make big to account for larger objects
    attr = '{}.scale'.format(snapPlane)
    for axis in ['X', 'Y', 'Z']:
        cmds.setAttr('{}{}'.format(attr,axis), 10000)

    # create temporary locator for origenting plane
    orientLocator = cmds.spaceLocator()
    attr = '{}.translate'.format(orientLocator[0])
    for i, axis in enumerate(['X', 'Y', 'Z']):
        cmds.setAttr('{}{}'.format(attr,axis), avgPosition[i])

    cmds.delete(cmds.orientConstraint(vertsObject, orientLocator, offset=(0,0,0)))
    cmds.move(avgNormal[0], avgNormal[1], avgNormal[2], orientLocator, r=1, os=1)

    # temporay orientation contraint
    cmds.delete(cmds.aimConstraint(orientLocator, snapPlaneParent, aimVector=[0,1,0]), orientLocator)

    # snap verts to plane
    cmds.select(snapPlane,vertList, r=1)

    cmds.select(snapPlane, r=1)
    cmds.makeLive()
    cmds.select(vertList, r=1)
    cmds.optionVar( iv=('polyConformAlongNormals', 0) )
    cmds.dR_DoCmd('conform')
    #cmds.makeLive(n=1)

    cmds.delete(snapPlaneParent)
    cmds.hilite(vertObject)

    print('Components flattened')
