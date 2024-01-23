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
# Last Updated : 2020/10/01

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

def bt_frameRateCounterShape(panelName, data):
    fps = cmds.headsUpDisplay('HUDFrameRate', q=True, sr=True)
    fpsValue = fps[0]

    #cmds.setAttr('polyDigits1.counter', float(fpsValue[:5]))
    if cmds.objExists('frameRateCounterShape') == True:
        cmds.undoInfo(swf=False)
        try:
            cmds.setAttr('frameRateCounterShape.text', 'Frame Rate:  ' + (fpsValue[:5]), type="string")
        finally:
            cmds.undoInfo(swf=True)

def bt_killFrameRateCallback():
    global frameRateCallback_Id
    try:
        om.MMessage.removeCallback( frameRateCallback_Id )
        print('Killing Frame Rate callback')
    except:
        print('No Frame Rate callback')

def bt_createFloatingFrameRate():
    global frameRateCallback_Id
    global frameRateScriptJob_Id

    #turn on default framerate HUD
    mel.eval('setFrameRateVisibility(1)')
    
    if cmds.objExists('frameRateCounterShape') == False:
        cmds.createNode('annotationShape', n='frameRateCounterShape')
        cmds.addAttr(longName='state', defaultValue=0, minValue=0, maxValue=1, attributeType='long')
        cmds.pickWalk(d='up')
        cmds.rename('frameRateCounter')
        
        cmds.setAttr ('frameRateCounterShape.text', 'Frame Rate', type="string")
        cmds.setAttr ('frameRateCounterShape.displayArrow', 0)
        cmds.setAttr ('frameRateCounterShape.overrideEnabled', 1)
        cmds.setAttr ('frameRateCounterShape.overrideRGBColors', 1)
        cmds.setAttr ('frameRateCounterShape.overrideColorRGB', 1, 1 ,1)

    # remove existing callback
    try:
        om.MMessage.removeCallback( frameRateCallback_Id )
    except:
        pass
    if cmds.objExists('frameRateCounterShape') == True:
        cmds.setAttr ('frameRateCounterShape.text', 'Frame Rate:  Disabled', type="string")

    if cmds.getAttr ('frameRateCounterShape.state') == 0:
        # create callback
        frameRateCallback_Id = omui.MUiMessage.add3dViewPostRenderMsgCallback( 'modelPanel4', bt_frameRateCounterShape )
        frameRateScriptJob_Id = cmds.scriptJob( runOnce=True, event=['NewSceneOpened', bt_killFrameRateCallback] )
        print('Enabling Frame Rate Counter.   Turn on Show->Dimensions in Panel to see.')
        cmds.inViewMessage( amg='Enabling floating Frame Rate counter.   Turn on Show->Dimensions in Panel to see.', pos='midCenter', fade=True)
        cmds.setAttr ('frameRateCounterShape.state', 1)
    else:
        print('Disabling Frame Rate Counter')
        cmds.inViewMessage( amg='Disabling floating Frame Rate counter', pos='midCenter', fade=True)
        cmds.setAttr ('frameRateCounterShape.state', 0)
        cmds.scriptJob( kill=frameRateScriptJob_Id, force=True)

if __name__ == "__main__":
    # create annotation node
    bt_createFloatingFrameRate()
