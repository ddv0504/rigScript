# Copyright(C) 1997-2020 Autodesk, Inc., and/or its licensors.
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
# Last updated: 2020/10/13
#
from maya.cmds import *

def bt_cleanupCurveMesh():

    select(filterExpand(sm=12),r=1)
    select(listRelatives(parent=True))
    meshes = ls(sl=1)
    if len(meshes) == 0:
        warning ('No meshes selected')
        return

    for mesh in meshes:

        instanceNode = ''
        extrudeNode = ''

        if attributeQuery('taper', exists=1, node=mesh):
            extrudeNode  = listConnections (mesh+'.taper')
            instanceNode = listConnections (extrudeNode[0]+'.path')[0]

        #delete remaining history and constraints
        delete(mesh, ch=1)
        delete(mesh, constraints=1)

        if attributeQuery ('width', exists=1, node=mesh):
            delete(listConnections (mesh+'.width'))
            deleteAttr (mesh+".width")

        if attributeQuery ('orientation', exists=1, node=mesh):
            delete(listConnections (mesh+'.orientation'))
            deleteAttr (mesh+".orientation")

        attrs = [ 'curvature', 'taper', 'twist', 'lengthDivisionSpacing', 'lengthDivisions', 'widthDivisions']
        for a in attrs:
            if attributeQuery(a, exists=1, node=mesh):
                deleteAttr('{}.{}'.format(mesh, a))

        if objExists(instanceNode):
            delete(instanceNode)



