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
#    Last Updated: 2020/10/07
#

import maya.cmds as cmds
import maya.api.OpenMaya as om

def bt_movePivotToFirstCV():
    curves = cmds.ls(sl=True)
    if len(curves) == 0:
        print('No curves selected.\n')
        return

    for c in curves:
        pt = cmds.pointPosition('{}.cv[0]'.format(c), w=1)

        selectionList = om.MSelectionList()
        selectionList.add(c)
        node = selectionList.getDependNode(0)

        origin = om.MPoint(pt)
        transform = om.MFnTransform(node)
        transform.setRotatePivot(origin, om.MSpace.kObject, False)
        transform.setScalePivot(origin, om.MSpace.kObject, False)
