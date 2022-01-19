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
'''
bt_zeroTransforms.py
adrian.graham@autodesk.com
02/18/2014

Description: Utility for freezing transforms on objects, including flushing
local pivot information into worldspace, which is essential for geo preparation
for systems such as Bullet.

Mode can be one of 'center', 'offset' or 'origin'
'''

import maya.cmds as cmds

def zero( node, translate=True, rotate=False, scale=True, mode='center' ):

    MODES=['center', 'offset', 'origin']
    ATTRS=[ 'tx', 'ty', 'tz', 'rz', 'ry', 'rz', 'sx', 'sy', 'sz' ]

    # There are a limited number of modes.
    if mode not in MODES:
        raise Exception("The 'mode' argument must be one of {}.".format(MODES))
    # end if

    # If any attrs are locked, skip.
    for attr in ATTRS:
        if cmds.getAttr('{}.{}'.format(node,attr), l=True ):
            cmds.warning( '{} has locked attributes. Skipping.'.format(node))
            return

    # If user specifies mode=origin, zero rotation as well.
    if mode == 'origin':
        rotate=True

    # Retain parent name.
    parent = None
    try:
        parent = cmds.listRelatives( node, p=True )[0]
    except:
        pass

    # Unparent, if not already under worldspace. Capture new name, in case node
    # is renamed on unparent.
    if parent:
        node = cmds.parent( node, w=True )[0]

    # Flush pivot info into worldspace.
    if mode == 'center':
        cmds.xform( node, ztp=True )

    # Query node type.
    shape_type = shapeType( node )

    # Find original location of object.
    old_pos = cmds.xform(node, q=True, ws=True, rp=True)

    # If centering pivot, we need to find the correct center of the bounding box.
    if mode == 'center':
        old_pos = findCenter( node )

        # Center pivot.
        cmds.xform( node, cp=True )

    # Move object back to the origin.
    cmds.move( 0, 0, 0, node, rpr=True )

    # Freeze node.
    cmds.makeIdentity(node, apply=True, t=translate, r=rotate, s=scale)

    # Move back to original position.
    cmds.xform(node, t=old_pos, ws=True)

    # If freezing at origin, place pivot at 0,0,0 and zero.
    if mode == 'origin':
        cmds.xform(
            node,
            piv=[0, 0, 0],
            ws=True,
        )

        # Freeze node.
        cmds.makeIdentity(
            node,
            apply=True,
            t=True,
            r=True,
            s=True
        )

    if parent:
        cmds.parent( node, parent )

def shapeType( node ):
    '''
    Returns the shape type of specified node. Be careful to return correct data
    for empty nulls and nodes with duplicate node names.
    '''
    if cmds.objectType( node ) != 'transform':
        return cmds.objectType( node )

    # Query shapes. If no shapes are gound, return the transform (i.e., it's an empty null).
    shapes = cmds.listRelatives( node, s=True, f=True )
    if not shapes:
        return 'transform'

    # If there are shapes, return the type of the zeroth shape.
    return cmds.objectType( shapes[0] )

def findCenter( node ):
    '''
    Query bounding box and calculate the center. This is necessary as the
    'objectCenter' command doesn't always work properly.
    '''

    bbx = cmds.xform( node, q=True, bb=True )

    # Calculate and return average position
    x = (bbx[3]+bbx[0])*0.5
    y = (bbx[4]+bbx[1])*0.5
    z = (bbx[5]+bbx[2])*0.5
    return [x, y, z]

# Interactive method. Iterates over list of nodes.
def run( mode='center' ):
    node_list = cmds.ls( sl=True )
    if not node_list:
        cmds.error( 'Select one or more nodes to zero its transforms.' )

    for node in node_list:
        zero( node=node, mode=mode )

    # Re-select original selection.
    cmds.select( node_list, r=True )

if __name__ == '__main__':
    run()
