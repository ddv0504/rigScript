# Copyright (C) 1997-2021 Autodesk, Inc., and/or its licensors.
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
# Autodesk non supported Python script
# Original Author : Hiroyuki Hag
# Last Updated: 2021/01/25
#
# Usage 1:
#  1. Select some UVs in UV shells which you want to align.
#  2. Execute bt_AlignUVShells() with directions 'left', 'right', 'bottom', or 'top'
#     For example, bt_AlignUVShells('left')
#
# Usage 2:
#  1. Execute bt_AlignUVShellsWindow()
#  2. Select some UVs in UV shells which you want to align.
#  3. Click direction button where your want align.
#

from builtins import range
import sys
if sys.version_info[0] < 3:
    from sets import Set

def bt_doAlignUVShells( direction ):
    import maya.cmds as cmds
    import maya.OpenMaya as om

    originalSelectionList = cmds.ls( sl = True )

    cmds.ConvertSelectionToUVs()
    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( selList )

    path = om.MDagPath()
    comp = om.MObject()
    selList.getDagPath( 0, path, comp )
    path.extendToShape()

    # Get UV comps
    uvCompFn = om.MFnSingleIndexedComponent( comp )
    uvComps = om.MIntArray()
    uvCompFn.getElements( uvComps )

    if path.apiType() == om.MFn.kMesh:
        meshFn = om.MFnMesh(path)
        util = om.MScriptUtil()
        uvShellIds = om.MIntArray()
        nbUvShells = util.asUintPtr()
        currentUVSet = cmds.polyUVSet( query=True, currentUVSet=True )

        meshFn.getUvShellsIds( uvShellIds, nbUvShells, currentUVSet[0] )

        shellSets = set([uvShellIds[uvComps[i]] for i in range(uvComps.length())])
        affectedShellIds = list(shellSets)

        # Get UV values
        u,v = om.MFloatArray(), om.MFloatArray()
        meshFn.getUVs( u, v, currentUVSet[0] )

        # Calculate Bounding Box
        bbmins = om.MPointArray()
        bbmaxs = om.MPointArray()

        for shellId in affectedShellIds:
            umin,umax = 1.0, 0.0
            vmin,vmax = 1.0, 0.0
            for j in range(len(uvShellIds)):
                if uvShellIds[j] == shellId :
                    umin = min(u[j],umin)
                    umax = max(u[j],umax)
                    vmin = min(v[j],vmin)
                    vmax = max(v[j],vmax)

            bbmins.append(om.MPoint(umin, vmin))
            bbmaxs.append(om.MPoint(umax, vmax))

        # Calculate offset based on the bounding box

        # Get smallest and largest x,y positions
        n = bbmins.length()
        bx = [ bbmins[i].x for i in range(n)]
        by = [ bbmins[i].y for i in range(n)]
        minPoint = om.MPoint(min(bx), min(by))

        n = bbmaxs.length()
        bx = [ bbmaxs[i].x for i in range(n)]
        by = [ bbmaxs[i].y for i in range(n)]
        maxPoint = om.MPoint(max(bx), max(by))

        # Get offset based on direction
        offsets = om.MPointArray()

        if direction == 'top':
            for i in range(bbmaxs.length()):
                offset = maxPoint - bbmaxs[i]
                offsets.append(om.MPoint(0., offset.y))

        elif direction == 'bottom':
            for i in range(bbmins.length()):
                offset = minPoint - bbmins[i]
                offsets.append(om.MPoint(0., offset.y))

        elif direction == 'right':
            for i in range(bbmaxs.length()):
                offset = maxPoint - bbmaxs[i]
                offsets.append(om.MPoint(offset.x, 0.))

        elif direction == 'left':
            for i in range(bbmins.length()):
                offset = minPoint - bbmins[i]
                offsets.append(om.MPoint(offset.x, 0.))

        # Move UVs
        for i in range(len(affectedShellIds)):
            selectionList = []
            for j in range(len(uvShellIds)):
                if uvShellIds[j] == affectedShellIds[i] :
                    selectionList.append('{}.map[{}]'.format(path.fullPathName(),j))

            cmds.select(selectionList)
            cmds.polyEditUVShell(relative=True, uValue=offsets[i].x , vValue=offsets[i].y)

    cmds.select( originalSelectionList )

def bt_alignUVShells(window_name='bt_AlignUVShellsWin'):
    import maya.cmds as cmds

    # If the window exists, delete it
    if cmds.window(window_name, ex=1):
        cmds.deleteUI(window_name, wnd=1)

    # Create a new window and connect the command callback to bt_doAlignUVShells
    assert(cmds.window(window_name, ex=1) == False)
    window=cmds.window(window_name, title='Align UV Shells', s=0)

    cmds.rowColumnLayout( w=300, nc=3 )

    cmds.separator(h=20, st='none')
    cmds.separator(h=20, st='none')
    cmds.separator(h=20, st='none')

    # Row 1
    cmds.separator(st='none')
    cmds.button( w=100, label= 'Top', c='bt_doAlignUVShells("top")' )
    cmds.separator(st='none')

    # Row 2
    cmds.button( w=100, label= 'Left', c='bt_doAlignUVShells("left")' )
    cmds.text(align='center', label='Align Shells', fn='boldLabelFont')
    cmds.button( w=100, label= 'Right', c='bt_doAlignUVShells("right")' )

    # Row 3
    cmds.separator(st='none')
    cmds.button( w=100, label= 'Bottom', c='bt_doAlignUVShells("bottom")' )
    cmds.separator(st='none')

    cmds.showWindow(window)

if __name__ == '__main__':
    bt_alignUVShells()