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
# based on create_pivot_bone script by Randall Hess 
# updated by Steven Roselle 01/09/19

import maya.cmds as cmds
import maya.api.OpenMaya as om
import bt_flattenComponentsUtils as utils

def bt_createObjectAtCustomPivotAxis(object='locator'):

    def snap(src, target):
        const = cmds.pointConstraint(target, src, mo=False, w=1.0)
        cmds.delete(const)
        const = cmds.orientConstraint(target, src, mo=False, w=1.0)
        cmds.delete(const)

    supported = ['locator', 'joint']
    if object not in supported:
        cmds.error('Requested object {} is not supported. Supported types should be one of {}'.format(object, supported))

    # Get manipulator pos and orient
    manip_pos = cmds.manipPivot(q=True, p=True)[0]
    manip_rot = cmds.manipPivot(q=True, o=True)[0]
    print(manip_rot)
    print(manip_pos)

    # store and clear selection
    selection = cmds.ls(sl=True)
    if len(selection) == 0:
        cmds.warning('Select a mesh object or component. Edit custom axis to desired position and orientation.')
        return
    cmds.select(cl=True)

    sel = selection[0]
    type = cmds.objectType(sel)
    print(type)

    # create temp locator and set pos/rot
    if object == 'locator':
        temp_loc = cmds.spaceLocator(n=object)[0]
        cmds.scale(.5,.5,.5)
    elif object == 'joint':
        temp_loc = cmds.joint(n=object)

    if type == 'transform':
        # If the selection is a transform, snap the locator to the pivot
        snap(temp_loc, sel)

    elif type == 'mesh':
        # If the selection is a mesh, find the parent (i.e., a transform)
        # and snap the locator to the pivot
        parent = cmds.listRelatives(sel, parent=True)
        snap(temp_loc, parent[0])

    # Rotate temp_loc if manip rot is not identity
    if not manip_rot == (0.0,0.0,0.0):
        for i,axis in enumerate(['X','Y','Z']):
            cmds.setAttr('{}.rotate{}'.format(temp_loc,axis), manip_rot[i])

    # move position to the cluster position
    if not manip_pos == (0.0,0.0,0.0):
        cmds.xform(temp_loc, ws=True, t=manip_pos)

    # get the position from the component selection
    types = ['mesh', 'transform']
    if type not in types:
        # get the transforms
        loc_xform = cmds.xform(temp_loc, q=True, m=True, ws=True)
        loc_rp = cmds.xform(temp_loc, q=True, ws=True, rp=True)

        cmds.select(selection, r=True)
        cmds.ConvertSelectionToVertices()
        try:
            cluster = cmds.cluster(n='temp_cluster')[1]
        except:
            cmds.warning('You must select a mesh object!')
            cmds.delete(temp_loc)
            return

        # get the cluster position
        cmds.select(cl=True)
        pos = cmds.xform(cluster, q=True, ws=True, rp=True)

        # snap to the cluster
        const = cmds.pointConstraint(cluster, temp_loc, mo=False, w=1.0)
        cmds.delete(const)

        cmds.delete(cluster)

        # rotate the temp_loc if manip rot has been modified
        if not manip_rot == (0.0,0.0,0.0):
            node = utils.nameToNode(temp_loc)
            transform = om.MFnTransform(node)
            transform.rotate(manip_rot, om.MSpace.kObject)

        # move position to the cluster position
        if not manip_pos == (0.0,0.0,0.0):
            cmds.xform(temp_loc, ws=True, t=manip_pos)

        # get the transforms
        loc_xform = cmds.xform(temp_loc, q=True, m=True, ws=True)
        loc_rp = cmds.xform(temp_loc, q=True, ws=True, rp=True)

    # unpin pivot
    cmds.manipPivot(pinPivot=False)
