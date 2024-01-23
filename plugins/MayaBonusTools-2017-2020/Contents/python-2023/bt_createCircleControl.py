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
# Author:   Steven T. L. Roselle
# 

import maya.cmds as cmds

def getOptionVarValue(name, default_value):
    if cmds.optionVar(ex=name):
        return cmds.optionVar(q=name)
    return default_value

def bt_resetSettings(*args):
    cmds.optionVar( iv=('bt_controlType', 1), )
    cmds.optionVar( iv=('bt_circleSize', 1), )
    cmds.optionVar( fv=('bt_circleR', 0), )
    cmds.optionVar( fv=('bt_circleG', 1), )
    cmds.optionVar( fv=('bt_circleB', 0), )
    cmds.optionVar( iv=('bt_circleOrient', 1), )
    cmds.warning('Close and reopen Create Circle Control window for reset settings to update')
    cmds.inViewMessage( amg='Close and reopen Create Circle Control window for reset settings to update.', pos='midCenter', fade=True )

def bt_setControlType(*args):
    controlType=cmds.radioButtonGrp('controlType', q=1, sl=1 )
    cmds.optionVar( iv=('bt_controlType', controlType), )

def bt_setCircleSize(*args):
    circleSize=cmds.floatSliderGrp('circleSize', q=1, v=1)
    cmds.optionVar( fv=('bt_circleSize', circleSize), )

def bt_setCircleRGB(*args):
    circleRGB=cmds.colorSliderGrp('circleRGB', q=1, rgb=1)
    cmds.optionVar( fv=('bt_circleR', circleRGB[0]), )
    cmds.optionVar( fv=('bt_circleG', circleRGB[1]), )
    cmds.optionVar( fv=('bt_circleB', circleRGB[2]), )

def bt_setCircleOrientation(*args):
    circleOrientation=cmds.radioButtonGrp('circleOrientation', q=1, sl=1 )
    cmds.optionVar( iv=('bt_circleOrient', circleOrientation), )

def bt_makeControl(*args):

    # Creates curve controls and align with selected joints

    # initialize type, size, color
    controlType = getOptionVarValue('bt_controlType', 1)
    circleSize = getOptionVarValue('bt_circleSize', 1)
    circleRGB = [getOptionVarValue('bt_circleR', 0), getOptionVarValue('bt_circleG', 1), getOptionVarValue('bt_circleB', 0)]
    circleOrientation = getOptionVarValue('bt_circleOrient', 1)

    if circleOrientation==2: # Y up
        xUp,yUp,zUp=0,1,0
    elif circleOrientation==3: # Z up
        xUp,yUp,zUp=0,0,1
    else: #default to X
        xUp,yUp,zUp=1,0,0

    selectedTransforms=cmds.ls(sl=1, tr=1) #filter for joints/transforms
    if len(selectedTransforms) == 0:
        cmds.warning( "No joints or transforms selected. Select 1 or more joints/transforms and try again." )

    else:
        # tag a control objects here
        for transform in selectedTransforms:
            # Create circle curve
            circleCurve=cmds.circle( normal=(xUp, yUp, zUp), radius=circleSize, center=(0, 0, 0), name='{}_controlCurve'.format(transform))

            # Create and attach controller node
            cmds.createNode('controller', n='{}_controlCurve_tag'.format(transform))
            cmds.connectAttr('{}_controlCurve.message'.format(transform), '{}_controlCurve_tag.controllerObject'.format(transform))

            # Set color for wireframe override 
            cmds.select(circleCurve)
            selected = cmds.ls(sl=True)
            shape = cmds.listRelatives(selected[0], s=True)
            cmds.select(shape)
            cmds.setAttr('{}.overrideEnabled'.format(shape[0]), True)
            cmds.setAttr('{}.overrideRGBColors'.format(shape[0]), True)
            cmds.setAttr('{}.overrideColorR'.format(shape[0]), circleRGB[0])
            cmds.setAttr('{}.overrideColorG'.format(shape[0]), circleRGB[1])
            cmds.setAttr('{}.overrideColorB'.format(shape[0]), circleRGB[2])

            offsetParent = cmds.group( circleCurve, name = '{}_controlOffset'.format(transform) )
            tmpParentConst = cmds.parentConstraint(transform, offsetParent, w=1, maintainOffset = False)
            cmds.delete (tmpParentConst[0])

            if(controlType == 2):
                #experimental - zero out t and r, move rot values to local axis
                #tmpRotX = cmds.getAttr(circleCurve[0]+'.rotateX')
                #tmpRotY = cmds.getAttr(circleCurve[0]+'.rotateY')
                #tmpRotZ = cmds.getAttr(circleCurve[0]+'.rotateZ')
                #cmds.setAttr(circleCurve[0]+'.rotateAxisX', tmpRotX)
                #cmds.setAttr(circleCurve[0]+'.rotateAxisY', tmpRotY)
                #cmds.setAttr(circleCurve[0]+'.rotateAxisZ', tmpRotZ)
                #cmds.setAttr(circleCurve[0]+'.rotateX', 0)
                #cmds.setAttr(circleCurve[0]+'.rotateY', 0)
                #cmds.setAttr(circleCurve[0]+'.rotateZ', 0)
                #cmds.select (circleCurve, r=1)
                #cmds.makeIdentity( apply=True, t=1, r=1, s=0, n=0, pn=1 )
                
                #constrain joint to curve
                cmds.parentConstraint(circleCurve, transform, w=1, maintainOffset=1)
            else:
                #parent curve shape under joint transform for direct connection
                cmds.select (circleCurve)
                selected = cmds.ls(sl=True)
                shape = cmds.listRelatives(selected[0], s=True)
                cmds.select(shape)
                tempShape = cmds.ls(sl=True)
                cmds.parent (tempShape, transform, r=1, s=1)
                cmds.delete (circleCurve)
                cmds.delete (offsetParent)

        # If contraint mode and if applying to a hierarchy then group control curves accordingly
        if(controlType == 2):
            for transform in selectedTransforms:
                parent=cmds.listRelatives (transform, parent=1)
                if parent == None:
                    continue

                parentCurve = '{}_controlCurve'.format(parent[0])
                if cmds.objExists(parentCurve) == False:
                    continue

                # Create hierarchy
                transformOffset = '{}_controlOffset'.format(transform)
                cmds.parent(transformOffset, parentCurve)

                # Create control nodes selection hierarchy
                cmds.controller(transformOffset, parentCurve, p=1)

        cmds.select(cl=1)
        numCurves = len(selectedTransforms)
        print('Created ', numCurves, 'control curves.')

def bt_createCircleControl(*args):
    # initialize type, size, color, and up-axis
    controlType = getOptionVarValue('bt_controlType', 1)
    circleSize = getOptionVarValue('bt_circleSize', 1)
    circleRGB = [getOptionVarValue('bt_circleR', 0), getOptionVarValue('bt_circleG', 1), getOptionVarValue('bt_circleB', 0)]
    circleOrientation = getOptionVarValue('bt_circleOrient', 1)

    # Setup UI
    if cmds.window('CircleControlWin', ex=1):
        cmds.deleteUI('CircleControlWin', wnd=1)
        #cmds.windowPref ('CircleControlWin', r=1)

    window=cmds.window( 'CircleControlWin', t="Create Circle Control", w=350, h=200, s=1,  mb=1 )

    cmds.menu( label='Edit', tearOff=False )
    cmds.menuItem( label='Reset Settings', command='bt_resetSettings()' )
    
    cmds.columnLayout( adj=1 )
    cmds.separator()
    cmds.text (' ')
    cmds.text ('Select one or more joints / transforms then apply to create circle controller for each.')
    cmds.text (' ')
    cmds.separator( st='single' )
    cmds.radioButtonGrp( 'controlType', l='Control Type:    ', cw=(2,150), la2=['Shape Under Transform', 'Parent Constraint'], nrb=2, sl=controlType , onc=bt_setControlType)
    cmds.floatSliderGrp( 'circleSize', l='Circle Size:    ', f=1, min=0.1, max=20.0, fmn=1.0, fmx=100.0, v=circleSize, dc=bt_setCircleSize, cc=bt_setCircleSize)
    cmds.colorSliderGrp( 'circleRGB', l='Circle Color:    ', rgb=circleRGB , dc=bt_setCircleRGB, cc=bt_setCircleRGB)
    cmds.radioButtonGrp( 'circleOrientation', l='Circle Orientation:    ', la3=['X Up', 'Y Up', 'Z Up'], nrb=3, sl=circleOrientation, onc=bt_setCircleOrientation )
    cmds.text (' ')
    cmds.setParent('..')

    cmds.columnLayout( adjustableColumn=1 )
    cmds.separator()
    cmds.setParent('..')

    cmds.rowColumnLayout(nc=3,co=(2,'both',5), adj=2 )
    cmds.button( l='Create Circle', w=150 , c=('bt_makeControl(), cmds.deleteUI(\"' + window + '\", window=1)') )
    cmds.button( l='Apply' , w=150, c=bt_makeControl )
    cmds.button( l='Close', w=150, c =('cmds.deleteUI(\"' + window + '\", window=1)') )
    cmds.setParent( '..' )

    cmds.showWindow( 'CircleControlWin' )

if __name__ == "__main__":
    # Open Create Circle Control UI
    bt_createCircleControl()