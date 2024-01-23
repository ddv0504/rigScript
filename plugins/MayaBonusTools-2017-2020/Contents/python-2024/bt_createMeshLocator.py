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
# Author: Steven T. L. Roselle
# Last Update: 2020/10/01
#

import maya.cmds as cmds

def bt_createMeshLocator():
    locObj = cmds.polyCube(w=0.2, h=0.2, d=0.2, name='polyLocator1')
    cmds.select(locObj,r=True)
    extNode = cmds.polyExtrudeFacet(kft=0, thickness=1)
    cmds.select(locObj,r=True)
    cmds.polySoftEdge(a=0, ch=1)
    cmds.select(locObj,r=True)
    cmds.setAttr('{}.displayHandle'.format(locObj[0]),1)

    cmds.addAttr(locObj[0],ln='length', min=.01, dv=1)
    lengthAttr = '{}.length'.format(locObj[0])
    cmds.setAttr(lengthAttr,keyable=1)

    cmds.addAttr(locObj[0],ln='thickness', min=.01, dv=0.1)
    thicknessAttr = '{}.thickness'.format(locObj[0])
    cmds.setAttr(thicknessAttr,keyable=1)

    cmds.connectAttr(lengthAttr,'{}.thickness'.format(extNode[0]))
    cmds.connectAttr(thicknessAttr,'{}.width'.format(locObj[1]))
    cmds.connectAttr(thicknessAttr,'{}.height'.format(locObj[1]))
    cmds.connectAttr(thicknessAttr,'{}.depth'.format(locObj[1]))

    if (cmds.objExists('locatorShader') == 1):
        print('\nUsing existing locatorShader\n')
    else:
        shader = cmds.shadingNode('lambert', asShader=1, name='locatorShader')
        cmds.setAttr('{}.colorR'.format(shader),0)
        cmds.setAttr('{}.colorG'.format(shader),0)
        cmds.setAttr('{}.colorB'.format(shader),1)

    cmds.select(locObj,r=True)
    cmds.hyperShade(assign='locatorShader')

if __name__ == '__main__':
    bt_createMeshLocator()
